import { Problem } from "./types.js";
export function scoreImpact(p:Problem):Problem{const sourceWeight=p.evidence.reduce((n,e)=>n+(e.source==="hubspot"?1.3:e.source==="fireflies"?1.15:1),0);const customerWeight=Math.min(2,p.customers.length*.4);p.impact=Math.min(100,Math.round((p.frequency*8+sourceWeight*7+customerWeight*15)*p.confidence));return p;}
