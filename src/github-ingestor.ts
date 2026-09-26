import {Event} from "./types.js";import {normalizeEvent} from "./unified-event-schema.js";
export function ingestGitHub(items:Array<{id?:string;title?:string;body?:string;customerId?:string;timestamp?:string}>):Event[]{return items.map(x=>normalizeEvent({id:x.id,source:"github",customerId:x.customerId,text:[x.title,x.body].filter(Boolean).join(" — "),timestamp:x.timestamp}));}
