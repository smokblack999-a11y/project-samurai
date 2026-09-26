import { Event, Source } from "./types.js";
export function normalizeEvent(input: Partial<Event> & {source:Source;text:string}): Event { return {id:input.id ?? crypto.randomUUID(),source:input.source,customerId:input.customerId,text:input.text.trim(),timestamp:input.timestamp ?? new Date().toISOString(),metadata:input.metadata ?? {}}; }
