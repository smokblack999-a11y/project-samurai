import {Event} from "./types.js";import {normalizeEvent} from "./unified-event-schema.js";
export function ingestFireflies(items:Array<{id?:string;summary?:string;customerId?:string;timestamp?:string}>):Event[]{return items.map(x=>normalizeEvent({id:x.id,source:"fireflies",customerId:x.customerId,text:x.summary??"",timestamp:x.timestamp}));}
