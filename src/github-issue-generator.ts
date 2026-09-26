import { Problem } from "./types.js";
export function githubIssue(p:Problem){return {title:"[X10THINC] "+p.title,body:"## Evidence\n"+p.evidence.map(e=>"- "+e.source+": "+e.text).join("\n")+"\n\n## Impact\n"+p.impact+"/100\n\n## Root cause\n"+(p.rootCause??"TBD")+"\n\n## Actions\n"+p.actions.map(a=>"- "+a).join("\n"),labels:["x10thinc","customer-impact"]};}
