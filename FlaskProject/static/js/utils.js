export function sanitizeSearchName(name) {
    return name.trim().toLowerCase().replace(/\b\w/g, char => char.toUpperCase());
}
