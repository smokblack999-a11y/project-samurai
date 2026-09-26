import { Problem } from "./types.js";
export function executiveReport(problems:Problem[]){return {generatedAt:new Date().toISOString(),totalProblems:problems.length,topProblems:problems.sort((a,b)=>b.impact-a.impact).slice(0,5).map(p=>({title:p.title,impact:p.impact,confidence:p.confidence,customers:p.customers.length,rootCause:p.rootCause,actions:p.actions}))};}
