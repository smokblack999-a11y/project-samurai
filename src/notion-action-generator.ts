import { Problem } from "./types.js";
export function notionActions(p:Problem):Problem{p.actions=["Validate with "+Math.max(1,p.customers.length)+" customer(s)","Reproduce or confirm the root cause","Ship the smallest measurable fix","Measure impact after release"];return p;}
