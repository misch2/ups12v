"""Procurement qualification calculations, with the accepted Phase3.6 allocations.

No CAD, native processes, output on import, or hardware measurement claims.
"""
import itertools
import json
import math
from pathlib import Path

EV=Path(__file__).resolve().parents[1]/'evidence/phase5-5-sourcing'


def feedback(top,bottom,top_tol,bottom_tol,top_ppm,bottom_ppm,delta_t=125):
    tt=top_tol+top_ppm*1e-6*delta_t
    bt=bottom_tol+bottom_ppm*1e-6*delta_t
    corners=[v*(1+top*a/(bottom*b))+i*top*a
             for v,a,b,i in itertools.product([.784,.816],[1-tt,1+tt],[1-bt,1+bt],[-.15e-6,.15e-6])]
    return dict(nominal_V=.8*(1+top/bottom),static_min_V=min(corners),static_max_V=max(corners),
                top_total_error_fraction=tt,bottom_total_error_fraction=bt,
                divider_current_A=.8/bottom,
                top_power_W=(.8*top/bottom)**2/top,bottom_power_W=.8**2/bottom,
                assumptions='Independent opposite tolerance+TCR from25C over125C; Vref0.784..0.816V; signed FB leakage +/-0.15uA SCREEN, not guaranteed limit')


def envelope(result,rail):
    if rail=='MCU':
        low=result['static_min_V']-.074-.020-.005-.005
        high=result['static_max_V']+.020+.005
        limits=(3.135,3.465)
    else:
        low=result['static_min_V']-.050-.020-.030-.010
        high=result['static_max_V']+.020+.010
        limits=(4.75,5.25)
    return dict(min_V=low,max_V=high,limits_V=limits,lower_reserve_V=low-limits[0],upper_reserve_V=limits[1]-high,
                pass_existing_allocation=low>=limits[0] and high<=limits[1])


def inductor(L_uH,vout_max,iout,dcr,Isat,drop,irms_rating):
    fs_min=450000*.94  # same accepted temperature sensitivity as Phase3.6
    Lmin=L_uH*1e-6*.8
    ripple=vout_max*(1-vout_max/18)/(fs_min*Lmin)
    rms=math.sqrt(iout*iout+ripple*ripple/12)
    hot=dcr*(1+.00393*100)
    saturation_sensitivity_ripple=ripple/(1-drop)
    return dict(Vin_max_V=18,Vout_max_V=vout_max,Iout_A=iout,frequency_min_screen_Hz=fs_min,
                inductance_nominal_uH=L_uH,inductance_tolerance_low_uH=Lmin*1e6,ripple_pp_A=ripple,
                peak_A=iout+ripple/2,valley_A=iout-ripple/2,rms_A=rms,
                DCR_max_25C_ohm=dcr,DCR_screen_125C_ohm=hot,
                copper_loss_25C_W=rms*rms*dcr,copper_loss_125C_W=rms*rms*hot,
                ripple_only_copper_25C_W=ripple*ripple/12*dcr,
                winding_loss_125C_Rac_over_Rdc_sensitivity_W={str(k):(iout*iout+k*ripple*ripple/12)*hot for k in [1,3,5]},
                core_loss_W=None,AC_winding_loss_measured=False,
                saturation_current_typical_A=Isat,saturation_drop_definition=drop,
                additional_decline_screen_peak_A=iout+saturation_sensitivity_ripple/2,
                additional_decline_screen_rms_A=math.sqrt(iout*iout+saturation_sensitivity_ripple**2/12),
                Irms_40C_rise_typical_A=irms_rating,
                HS_minimum_current_limit_A=4.2,LS_minimum_VALLEY_limit_A=2.9,
                HS_maximum_current_limit_A=5.8,
                normal_peak_below_HS_minimum=iout+ripple/2<4.2,
                normal_rms_below_40C_rating=rms<irms_rating,
                note='Normal-load calculation, not hot-fault guarantee. Isat/Irms are typical25C values. 155C component maximum includes self-heating. Core/Rac data at actual ripple unavailable; no measured thermal claim.')


def main():
    main_original=feedback(31600,10000,.001,.001,10,10)
    main_viking_original_bottom=feedback(31600,10000,.001,.001,25,10)
    main_both_25=feedback(31600,10000,.001,.001,25,25)
    main_proposed=feedback(31600,10000,.001,.0002,25,10)
    f5_original=feedback(53000,10000,.001,.001,25,25)
    f5_proposed=feedback(16000,3010,.001,.001,25,25)
    assert abs(envelope(main_original,'MCU')['min_V']-3.14159)<.00002
    assert not envelope(main_both_25,'MCU')['pass_existing_allocation']
    assert envelope(main_proposed,'MCU')['pass_existing_allocation']
    assert envelope(f5_proposed,'F5')['pass_existing_allocation']
    result=dict(type='CALCULATIONS_NOT_HARDWARE_MEASUREMENTS',
                basis='Same explicit allocations as evidence/verify_phase3_6.py, no new acceptance gates',
                feedback={name:dict(**r,envelope=envelope(r,'MCU' if name.startswith('MAIN') else 'F5')) for name,r in [
                    ('MAIN_original_10ppm',main_original),('MAIN_R32_25_R33_10ppm',main_viking_original_bottom),
                    ('MAIN_both_25ppm_REJECT',main_both_25),('MAIN_Viking_and_RESI_PROPOSED',main_proposed),
                    ('F5_original_53k_10k',f5_original),('F5_proposed_16k_3k01',f5_proposed)]},
                inductors={'L2':inductor(4.7,main_proposed['static_max_V'],1,.0363,7,.4,5.9),
                           'L3':inductor(6.8,f5_proposed['static_max_V'],2,.0286,7.8,.3,6.4)},
                copper_skin_depth_mm_at_423kHz=math.sqrt(1.724e-8/(math.pi*423000*4*math.pi*1e-7))*1000,
                additional_F5_divider_current_A=f5_proposed['divider_current_A']-f5_original['divider_current_A'])
    (EV/'electrical-calculations.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:{'nominal_V':v['nominal_V'],'envelope':v['envelope']} for k,v in result['feedback'].items()}))
    print(json.dumps({k:{p:v[p] for p in ['ripple_pp_A','peak_A','rms_A','copper_loss_125C_W']} for k,v in result['inductors'].items()}))

if __name__=='__main__':main()
