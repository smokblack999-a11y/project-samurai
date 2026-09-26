export type Source = "github" | "fireflies" | "hubspot" | "notion";
export interface Event { id:string; source:Source; customerId?:string; text:string; timestamp:string; metadata?:Record<string,unknown>; }
export interface Problem { id:string; title:string; evidence:Event[]; customers:string[]; frequency:number; impact:number; confidence:number; rootCause?:string; actions:string[]; }
