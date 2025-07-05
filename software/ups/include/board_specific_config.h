// dynamically include board-specific config
// clang-format off
#define STRINGIFY(x) STR(x)
#define STR(x) #x
#define EXPAND(x) x
#define CONCAT3(a, b, c) STRINGIFY(EXPAND(a)EXPAND(b)EXPAND(c))
#include CONCAT3(boards/,BOARD_CONFIG,.h)
// clang-format on
