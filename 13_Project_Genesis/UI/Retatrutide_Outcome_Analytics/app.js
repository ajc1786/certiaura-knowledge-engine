"use strict";
const output=document.getElementById("output");
function loadFile(event){const file=event.target.files[0];if(!file){return;}const reader=new FileReader();reader.onload=()=>{try{const value=JSON.parse(String(reader.result));output.textContent=JSON.stringify(value,null,2);}catch(error){output.textContent="Invalid JSON: "+error.message;}};reader.readAsText(file);}
document.getElementById("analytics").addEventListener("change",loadFile);
document.getElementById("alert").addEventListener("change",loadFile);
