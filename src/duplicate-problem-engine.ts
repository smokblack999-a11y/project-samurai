import { Problem } from "./types.js";
export function dedupeProblems(items:Problem[]):Problem[]{const out:Problem[]=[];for(const p of items){const hit=out.find(x=>similar(x.title,p.title));if(hit){hit.evidence.push(...p.evidence);hit.frequency+=p.frequency;}else out.push({...p});}return out;}
function similar(a:string,b:string){const A=new Set(a.toLowerCase().split(/\\W+/).filter(Boolean));const B=new Set(b.toLowerCase().split(/\\W+/).filter(Boolean));const inter=[...A].filter(x=>B.has(x)).length;return inter/Math.max(1,Math.min(A.size,B.size))>=.6;}
