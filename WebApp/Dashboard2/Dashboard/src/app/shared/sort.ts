export type SortDir = 'asc' | 'desc';
export interface SortState<T> { by: keyof T & string; dir: SortDir; }

export function makeSorter<T>(
  state: SortState<T>,
  accessors: Record<string, (r: T) => unknown>
) {
  const get = accessors[state.by];
  return (a: T, b: T) => {
    const av = norm(get?.(a));
    const bv = norm(get?.(b));
    const res = av > bv ? 1 : av < bv ? -1 : 0;
    return state.dir === 'asc' ? res : -res;
  };
}

function norm(v: unknown) {
  if (v == null) return '';
  return typeof v === 'string' ? v.toLowerCase() : v;
}
