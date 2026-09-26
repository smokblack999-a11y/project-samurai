import {Event} from "./types.js";import {normalizeEvent} from "./unified-event-schema.js";
export function ingestHubSpot(items:Array<{id?:string;note?:string;customerId?:string;timestamp?:string}>):Event[]{return items.map(x=>normalizeEvent({id:x.id,source:"hubspot",customerId:x.customerId,text:x.note??"",timestamp:x.timestamp}));}
