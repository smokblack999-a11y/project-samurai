export function beforeAfter(before:number,after:number){const delta=after-before;return {before,after,delta,percent:before===0?null:Math.round(delta/before*100)};}
