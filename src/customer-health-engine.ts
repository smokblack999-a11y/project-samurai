import { Event } from "./types.js";
export function customerHealth(events:Event[]){const m=new Map<string,number>();for(const e of events){if(!e.customerId)continue;const delta=e.source==="hubspot"?1:e.source==="fireflies"?-1:0;m.set(e.customerId,Math.max(0,50+(m.get(e.customerId)??0)+delta));}return Object.fromEntries(m);}
