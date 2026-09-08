#ifndef WEAR_NATIVE_TYPES_H
#define WEAR_NATIVE_TYPES_H

/* Native Stage-0 migration contract for deterministic symbol/type tracking. */
typedef enum {
    WEAR_TYPE_UNKNOWN = 0,
    WEAR_TYPE_INT = 1,
    WEAR_TYPE_STR = 2,
    WEAR_TYPE_ERROR = 3
} WearType;

/* Keep type identity independent from identifier spelling. */
static inline const char* wear_type_name(WearType type) {
    switch (type) {
        case WEAR_TYPE_INT: return "int";
        case WEAR_TYPE_STR: return "str";
        case WEAR_TYPE_ERROR: return "error";
        default: return "unknown";
    }
}

#endif /* WEAR_NATIVE_TYPES_H */
