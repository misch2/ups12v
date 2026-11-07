"""Exact approved Phase4.8A IPC footprint preparation; import-safe, no CAD file writes."""
from pathlib import Path
from .safety import require,read_json,digest

POSITIONS={'L2':[49.65,85,-90],'C37':[50.9,79.5,-90],'C33':[54,85,90],'C45':[56.4,85,90]}
PLAN_SHA='dd4b7d7a107e6d4893db032d17910c8783cde8d36dd21ad93146c13b6867be74'
CANDIDATE_SHA='36687b95ad648042563c7f8700f01b0f3da8fcde15e35da4071fedb273c81de2'


def check_candidate(plan_path,candidate):
    plan=read_json(plan_path);candidate=Path(candidate)
    require(digest(plan_path)==PLAN_SHA,'Approved U3 plan hash differs; STOP')
    require(plan==read_json(candidate/'plan.json'),'Scratch plan differs; STOP')
    require(digest(candidate/'ups12v_v4.kicad_pcb')==CANDIDATE_SHA,'Accepted scratch board differs; STOP')
    require(plan.get('placements')==POSITIONS and len(plan['tracks'])==68 and len(plan['vias'])==11,
            'Approved U3 geometry/counts differ; STOP')
    return plan


def prepare_footprints(footprints,plan,native_candidate):
    from kipy.board_types import FootprintInstance,Footprint3DModel,Field
    from kipy.geometry import Vector2,Angle
    from google.protobuf.json_format import MessageToDict
    expected_native=read_json(Path(native_candidate)/'final-snapshot.json')
    byref={p['ref']:p for p in expected_native['footprints'].values()}
    native_pads=expected_native['pads'];updates=[]
    for original in footprints:
        ref=original.reference_field.text.value
        if ref not in POSITIONS:continue
        fp=FootprintInstance(original.proto)
        def identity(i):
            if hasattr(i.proto,'id'):return i.proto.DESCRIPTOR.full_name,i.proto.id.SerializeToString()
            require(isinstance(i,Footprint3DModel),'Unsupported footprint child; STOP')
            return i.proto.DESCRIPTOR.full_name,i.proto.SerializeToString()
        identities=lambda items:{identity(i) for i in items}
        ids=identities(fp.definition.items)
        models=[(i,item) for i,item in enumerate(fp.definition.items) if isinstance(item,Footprint3DModel)]
        x,y,a=plan['placements'][ref]
        # Exact90-degree integer rotation avoids the SDK's float-to-int1nm
        # truncation of graphical endpoints. Only pure in-memory preparation
        # uses this override; no IPC command runs inside it, and it is restored.
        old_rotate=Vector2.rotate
        def quarter_rotate(vector,angle,center):
            turns=round(angle.degrees/90)
            require(abs(angle.degrees-turns*90)<1e-10,'Only orthogonal approved rotations supported; STOP')
            dx,dy=vector.x-center.x,vector.y-center.y
            for _ in range(turns%4):dx,dy=dy,-dx
            vector.x=center.x+dx;vector.y=center.y+dy
            return vector
        try:
            Vector2.rotate=quarter_rotate
            fp.orientation=Angle.from_degrees(a)
        finally:
            Vector2.rotate=old_rotate
        # The installed SDK omits model wrappers from its rotation loop. Their
        # offsets/rotations are footprint-local: retain them verbatim in order.
        items=list(fp.definition.items)
        for i,item in models:items.insert(i,item)
        fp.definition.items=items
        fp.position=Vector2.from_xy(round(x*1e6),round(y*1e6))
        for pad in fp.definition.pads:
            pad.padstack.angle=Angle.from_degrees(pad.padstack.angle.degrees%360)
        for item in fp.texts_and_fields:
            text=item.text if isinstance(item,Field) else item
            text.attributes.angle=text.attributes.angle%360
        require(ids==identities(fp.definition.items),f'Footprint children changed: {ref}; STOP')
        require(byref[ref]['position']==[fp.position.x/1e6,fp.position.y/1e6]
                and byref[ref]['angle']==fp.orientation.degrees,f'Footprint target differs: {ref}; STOP')
        for pad in fp.definition.pads:
            target=native_pads[pad.id.value]
            require(target['position']==[pad.position.x/1e6,pad.position.y/1e6],
                    f'Pad target differs: {ref}.{target["pin"]}; STOP')
        updates.append(fp)
    require(len(updates)==4,'Exactly four live footprints required; STOP')
    verify_artwork(updates,native_candidate)
    return updates


def verify_artwork(footprints,native_candidate):
    from google.protobuf.json_format import MessageToDict
    audit=read_json(Path(native_candidate)/'native-audit.json')['footprint_graphics']
    def point(value):return [int(value.get('xNm',0))/1e6,int(value.get('yNm',0))/1e6]
    for fp in footprints:
        ref=fp.reference_field.text.value;expected=audit[ref]
        for field in [fp.reference_field,fp.value_field]:
            text=field.text;native=expected[text.id.value]
            require([text.position.x/1e6,text.position.y/1e6]==native['GetPosition']
                    and text.attributes.angle%360==native['text_angle']%360
                    and text.value==native['GetText'],f'Field target differs: {ref}; STOP')
        for item in fp.definition.items:
            row=MessageToDict(item.proto)
            if 'shape' not in row:continue
            native=expected[row['id']['value']];shape=row['shape']
            require(int(shape['attributes']['stroke']['width']['valueNm'])==native['GetWidth'],
                    f'Artwork stroke differs: {ref}; STOP')
            if 'segment' in shape:points=shape['segment'];keys=['start','end']
            else:
                require('rectangle' in shape,'Unsupported approved artwork shape; STOP')
                points=shape['rectangle'];keys=['topLeft','bottomRight']
            require(point(points[keys[0]])==native['GetStart'] and point(points[keys[1]])==native['GetEnd'],
                    f'Artwork target differs: {ref}; STOP')


def expected_capture(before,updates):
    import copy
    from google.protobuf.json_format import MessageToDict
    result=copy.deepcopy(before)
    for fp in updates:
        result['footprints'][fp.id.value]=MessageToDict(fp.proto)
        for pad in fp.definition.pads:
            result['pads'][pad.id.value]=MessageToDict(pad.proto)
    return result
