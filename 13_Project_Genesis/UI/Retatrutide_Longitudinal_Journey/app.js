"use strict";
const memory={journey:null,schedule:null,handoff:null};
const status=document.getElementById("status");const output=document.getElementById("output");
function text(tag,value,className){const node=document.createElement(tag);node.textContent=value;if(className)node.className=className;return node;}
function render(){output.replaceChildren();for(const key of ["journey","schedule","handoff"]){if(!memory[key])continue;const card=text("article","","card"+(JSON.stringify(memory[key]).includes("URGENT")?" urgent":""));card.append(text("h2",key[0].toUpperCase()+key.slice(1)));card.append(text("pre",JSON.stringify(memory[key],null,2)));output.append(card);}status.textContent=Object.values(memory).filter(Boolean).length+" pseudonymised file(s) loaded in memory.";}
async function load(key,file){if(!file)return;const data=JSON.parse(await file.text());const serialised=JSON.stringify(data);if(/@|(?:\+?44\s?7\d{3}|07\d{3})[\s-]?\d{3}[\s-]?\d{3}/i.test(serialised)){throw new Error("Potential direct identifier detected.");}memory[key]=data;render();}
for(const key of ["journey","schedule","handoff"]){document.getElementById(key).addEventListener("change",async event=>{try{await load(key,event.target.files[0]);}catch(error){status.textContent=error.message;event.target.value="";}});}
document.getElementById("clear").addEventListener("click",()=>{memory.journey=null;memory.schedule=null;memory.handoff=null;document.querySelectorAll("input[type=file]").forEach(x=>x.value="");render();});render();
