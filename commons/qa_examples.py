from commons.types import Topics


def get_persona_question_examples(topic: Topics) -> str:
    if topic == Topics.GAMES:
        return _get_game_question_examples()
    if topic == Topics.SCIENCE:
        return _get_science_question_examples()
    if topic == Topics.ANIMATION:
        return _get_animation_question_examples()


def get_answer_examples(topic: Topics) -> str:
    if topic == Topics.GAMES:
        return _get_game_answer_examples()
    if topic == Topics.ANIMATION:
        return _get_animation_answer_examples()
    if topic == Topics.SCIENCE:
        return _get_science_answer_examples()

    # deprecated examples below
    # EXAMPLE_OUTPUTS = """
    # <example_question_1>:
    # "Create a Solar System Orbit Simulator using JavaScript, HTML, and CSS. The simulator should display the Sun at the center of the screen and at least 4 planets orbiting around it.
    #     Requirements:
    #     1. Implement a slider that controls the speed of the planets' orbits. The slider should allow users to adjust the simulation speed from very slow to very fast.

    #     2. Add a feature that allows users to click on a planet to display its name and basic information (e.g., size, distance from the Sun) in a small pop-up or sidebar.

    #     3. Include a button that toggles the visibility of planet orbit paths. When enabled, it should show the elliptical paths of the planets' orbits.

    #     Ensure that the planets' sizes and distances are proportional (though not necessarily to scale) to represent the relative differences in the solar system. Use only built-in JavaScript libraries and features for this implementation.
    #     Note:
    #     - The visualization should be implemented in JavaScript with HTML and CSS.
    #     - Ensure that the output has both index.js and index.html files",
    # </example_question_1>:

    # <example_answer_1>
    # {
    #     "files": [
    #         {
    #             "filename": "index.js",
    #             "content": "const canvas=document.getElementById("canvas");const ctx=canvas.getContext("2d");const speedSlider=document.getElementById("speed");const toggleOrbitsBtn=document.getElementById("toggleOrbits");const infoDiv=document.getElementById("info");let width=(canvas.width=window.innerWidth);let height=(canvas.height=window.innerHeight);let centerX=width/2;let centerY=height/2;let showOrbits=false;const planets=[{name:"Mercury",color:"#8c7e6d",radius:5,distance:60,speed:0.04,angle:0,info:"Smallest planet, closest to Sun"},{name:"Venus",color:"#e3bb76",radius:8,distance:100,speed:0.015,angle:0,info:"Hottest planet, rotates backwards"},{name:"Earth",color:"#4f94cd",radius:9,distance:150,speed:0.01,angle:0,info:"Our home planet, supports life"},{name:"Mars",color:"#c1440e",radius:7,distance:200,speed:0.008,angle:0,info:"The Red Planet, has polar ice caps"}];function drawSun(){ctx.beginPath();ctx.arc(centerX,centerY,20,0,Math.PI*2);ctx.fillStyle="#ffd700";ctx.fill();}function drawPlanet(planet){const x=centerX+Math.cos(planet.angle)*planet.distance;const y=centerY+Math.sin(planet.angle)*planet.distance;if(showOrbits){ctx.beginPath();ctx.arc(centerX,centerY,planet.distance,0,Math.PI*2);ctx.strokeStyle="rgba(255, 255, 255, 0.2)";ctx.stroke();}ctx.beginPath();ctx.arc(x,y,planet.radius,0,Math.PI*2);ctx.fillStyle=planet.color;ctx.fill();}function updatePlanets(){const speed=parseFloat(speedSlider.value);planets.forEach((planet)=>{planet.angle+=planet.speed*speed;});}let stars=[];function initStars(){stars=[];for(let i=0;i<200;i++){stars.push({x:Math.random()*width,y:Math.random()*height,size:Math.random()*1.5,speed:Math.random()*0.08+0.01});}}function drawStars(){ctx.fillStyle="#ffffff";for(const star of stars){ctx.beginPath();ctx.arc(star.x,star.y,star.size,0,Math.PI*2);ctx.fill();star.y+=star.speed;if(star.y>height){star.y=0;star.x=Math.random()*width;}}}function animate(){ctx.clearRect(0,0,width,height);drawStars();drawSun();planets.forEach(drawPlanet);updatePlanets();requestAnimationFrame(animate);}function handleResize(){width=canvas.width=window.innerWidth;height=canvas.height=window.innerHeight;centerX=width/2;centerY=height/2;initStars();}function showPlanetInfo(event){const rect=canvas.getBoundingClientRect();const mouseX=event.clientX-rect.left;const mouseY=event.clientY-rect.top;for(const planet of planets){const planetX=centerX+Math.cos(planet.angle)*planet.distance;const planetY=centerY+Math.sin(planet.angle)*planet.distance;const distance=Math.sqrt((mouseX-planetX)**2+(mouseY-planetY)**2);if(distance<=planet.radius){infoDiv.innerHTML=`<h3>${planet.name}</h3><p>${planet.info}</p>`;infoDiv.style.display="block";return;}}infoDiv.style.display="none";}toggleOrbitsBtn.addEventListener("click",()=>{showOrbits=!showOrbits;});canvas.addEventListener("click",showPlanetInfo);window.addEventListener("resize",handleResize);initStars();animate();//# sourceMappingURL=index.js.map",
    #             "language": "javascript"
    #         },
    #         {
    #             "filename": "index.html",
    #             "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><title>Solar System Orbit Simulator</title><style>body{background-color:#000;margin:0;font-family:Arial,sans-serif;overflow:hidden}#canvas{display:block}#controls{color:#fff;position:absolute;top:10px;left:10px}#info{color:#fff;background-color:#000000b3;border-radius:5px;padding:10px;display:none;position:absolute;top:10px;right:10px}.slider{width:200px}</style></head><body><canvas id="canvas"></canvas><div id="controls"><label for="speed">Orbit Speed:</label><input type="range" id="speed" class="slider" min="0.1" max="5" step="0.1" value="1" /><button id="toggleOrbits">Toggle Orbit Paths</button></div><div id="info"></div><script src="./index.js"></script></body></html>",
    #             "language": "html"
    #         }
    #     ],
    #     "installation_commands": "null",
    #     "additional_notes": "The code uses built-in libraries so no additional commands are required."
    # }
    # </example_answer_1>

    # <example_question_2>:
    #   "Create a web page that displays an interactive piano visualization using HTML, CSS, and JavaScript. The piano should have 88 keys (52 white keys and 36 black keys). Implement the following user interactions:

    #   1. When the user hovers over a key, it should visually highlight to indicate it can be played.

    #   2. Clicking on a key should produce a pressing animation and play a corresponding piano note sound.

    #   3. Implement a slider that adjusts the piano's volume, affecting the loudness of the notes played when keys are clicked.

    #   Ensure the visualization is responsive and works well on different screen sizes. Use only built-in JavaScript libraries and features for this implementation.
    #   Note:
    #   - The visualization should be implemented in JavaScript with HTML and CSS.
    #   - Ensure that the output has both index.js and index.html files"
    # </example_question_2>

    # <example_answer_2>
    # {
    #     "files": [
    #         {
    #             "filename": "index.js",
    #             "content": "const pianoKeys = [{note: 'A0', type: 'white'}, {note: 'A#0', type: 'black'}, {note: 'B0', type: 'white'}, {note: 'C1', type: 'white'}, {note: 'C#1', type: 'black'}, {note: 'D1', type: 'white'}, {note: 'D#1', type: 'black'}, {note: 'E1', type: 'white'}, {note: 'F1', type: 'white'}, {note: 'F#1', type: 'black'}, {note: 'G1', type: 'white'}, {note: 'G#1', type: 'black'}, {note: 'A1', type: 'white'}, {note: 'A#1', type: 'black'}, {note: 'B1', type: 'white'}, {note: 'C2', type: 'white'}, {note: 'C#2', type: 'black'}, {note: 'D2', type: 'white'}, {note: 'D#2', type: 'black'}, {note: 'E2', type: 'white'}, {note: 'F2', type: 'white'}, {note: 'F#2', type: 'black'}, {note: 'G2', type: 'white'}, {note: 'G#2', type: 'black'}, {note: 'A2', type: 'white'}, {note: 'A#2', type: 'black'}, {note: 'B2', type: 'white'}, {note: 'C3', type: 'white'}, {note: 'C#3', type: 'black'}, {note: 'D3', type: 'white'}, {note: 'D#3', type: 'black'}, {note: 'E3', type: 'white'}, {note: 'F3', type: 'white'}, {note: 'F#3', type: 'black'}, {note: 'G3', type: 'white'}, {note: 'G#3', type: 'black'}, {note: 'A3', type: 'white'}, {note: 'A#3', type: 'black'}, {note: 'B3', type: 'white'}, {note: 'C4', type: 'white'}, {note: 'C#4', type: 'black'}, {note: 'D4', type: 'white'}, {note: 'D#4', type: 'black'}, {note: 'E4', type: 'white'}, {note: 'F4', type: 'white'}, {note: 'F#4', type: 'black'}, {note: 'G4', type: 'white'}, {note: 'G#4', type: 'black'}, {note: 'A4', type: 'white'}, {note: 'A#4', type: 'black'}, {note: 'B4', type: 'white'}, {note: 'C5', type: 'white'}, {note: 'C#5', type: 'black'}, {note: 'D5', type: 'white'}, {note: 'D#5', type: 'black'}, {note: 'E5', type: 'white'}, {note: 'F5', type: 'white'}, {note: 'F#5', type: 'black'}, {note: 'G5', type: 'white'}, {note: 'G#5', type: 'black'}, {note: 'A5', type: 'white'}, {note: 'A#5', type: 'black'}, {note: 'B5', type: 'white'}, {note: 'C6', type: 'white'}, {note: 'C#6', type: 'black'}, {note: 'D6', type: 'white'}, {note: 'D#6', type: 'black'}, {note: 'E6', type: 'white'}, {note: 'F6', type: 'white'}, {note: 'F#6', type: 'black'}, {note: 'G6', type: 'white'}, {note: 'G#6', type: 'black'}, {note: 'A6', type: 'white'}, {note: 'A#6', type: 'black'}, {note: 'B6', type: 'white'}, {note: 'C7', type: 'white'}, {note: 'C#7', type: 'black'}, {note: 'D7', type: 'white'}, {note: 'D#7', type: 'black'}, {note: 'E7', type: 'white'}, {note: 'F7', type: 'white'}, {note: 'F#7', type: 'black'}, {note: 'G7', type: 'white'}, {note: 'G#7', type: 'black'}, {note: 'A7', type: 'white'}, {note: 'A#7', type: 'black'}, {note: 'B7', type: 'white'}, {note: 'C8', type: 'white'}]; const piano = document.getElementById('piano'); const volumeSlider = document.getElementById('volumeSlider'); let audioContext; function createKey(note, type) { const key = document.createElement('div'); key.className = `key ${type}-key`; key.dataset.note = note; key.addEventListener('mousedown', playNote); key.addEventListener('mouseup', stopNote); key.addEventListener('mouseleave', stopNote); return key; } function initializePiano() { pianoKeys.forEach(key => { piano.appendChild(createKey(key.note, key.type)); }); } function playNote(event) { if (!audioContext) { audioContext = new (window.AudioContext || window.webkitAudioContext)(); } const note = event.target.dataset.note; const frequency = getFrequency(note); const oscillator = audioContext.createOscillator(); const gainNode = audioContext.createGain(); oscillator.type = 'sine'; oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime); gainNode.gain.setValueAtTime(parseFloat(volumeSlider.value), audioContext.currentTime); gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 1); oscillator.connect(gainNode); gainNode.connect(audioContext.destination); oscillator.start(); oscillator.stop(audioContext.currentTime + 1); event.target.classList.add('active'); } function stopNote(event) { event.target.classList.remove('active'); } function getFrequency(note) { const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']; const octave = parseInt(note.slice(-1)); const semitone = notes.indexOf(note.slice(0, -1)); return 440 * Math.pow(2, (octave - 4) + (semitone - 9) / 12); } initializePiano();",
    #             "language": "javascript"
    #         },
    #         {
    #             "filename": "index.html",
    #             "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Interactive Piano Visualization</title><style>body{background:linear-gradient(#1a2a6c,#b21f1f,#fdbb2d);justify-content:center;align-items:center;min-height:100vh;margin:0;padding:0;font-family:Arial,sans-serif;display:flex}.piano-container{background-color:#222;border-radius:10px;padding:20px;box-shadow:0 0 20px #00000080}.piano{display:flex;position:relative}.key{cursor:pointer;transition:all .1s;position:relative}.white-key{z-index:1;background:linear-gradient(#f0f0f0,#fff);border:1px solid #ccc;border-radius:0 0 5px 5px;width:40px;height:200px}.black-key{z-index:2;background:linear-gradient(#333,#000);border-radius:0 0 3px 3px;width:25px;height:120px;margin-left:-12.5px;margin-right:-12.5px}.white-key:hover{background:linear-gradient(#e0e0e0,#f5f5f5)}.black-key:hover{background:linear-gradient(#444,#222)}.white-key:active,.white-key.active{background:linear-gradient(#d0d0d0,#e5e5e5);transform:translateY(2px)}.black-key:active,.black-key.active{background:linear-gradient(#555,#333);transform:translateY(2px)}.volume-control{color:#fff;justify-content:center;align-items:center;margin-top:20px;display:flex}.volume-slider{width:200px;margin:0 10px}</style></head><body><div class="piano-container"><div class="piano" id="piano"></div><div class="volume-control"><span>Volume:</span><input type="range" min="0" max="1" step="0.1" value="0.5" class="volume-slider" id="volumeSlider"></div></div><script src="/index.js"></script></body></html>",
    #             "language": "html"
    #         }
    #     ],
    #     "installation_commands": "null",
    #     "additional_notes": "The code uses built-in libraries so no additional commands are required."
    # },
    # </example_answer_2>

    # <example_question_3>
    # "Create a web page that visualizes a desert landscape using HTML, CSS, and JavaScript. The visualization should include sand dunes, a sun, and at least one cactus. Implement the following interactive features:

    # 1. When the user moves their mouse across the screen, small dust particles should appear and follow the mouse movement, simulating a light breeze in the desert.

    # 2. Allow the user to click anywhere on the screen to 'plant' a new cactus at that location. The cactus should grow from small to full size over a short period of time.

    # Ensure that the visualization is responsive and works well on different screen sizes. Use only built-in JavaScript functions and avoid external libraries.
    # Note:
    # - The visualization should be implemented in JavaScript with HTML and CSS.
    # - Ensure that the output has both index.js and index.html files"
    # </example_question_3>

    # <example_answer_3>
    # {
    # "files": [
    #     {
    #         "filename": "index.js",
    #         "content": "document.addEventListener("DOMContentLoaded",()=>{const desert=document.getElementById("desert");const dustParticles=[];createCactus(window.innerWidth/2,window.innerHeight*0.7);desert.addEventListener("mousemove",(e)=>{createDustParticle(e.clientX,e.clientY)});desert.addEventListener("click",(e)=>{createCactus(e.clientX,e.clientY)});function createCactus(x,y){const cactus=document.createElement("div");cactus.className="cactus";cactus.style.left=`${x}px`;cactus.style.bottom=`${window.innerHeight-y}px`;cactus.style.height="0px";desert.appendChild(cactus);setTimeout(()=>{cactus.style.height="100px"},50)}function createDustParticle(x,y){const dust=document.createElement("div");dust.className="dust";dust.style.left=`${x}px`;dust.style.top=`${y}px`;desert.appendChild(dust);dustParticles.push(dust);if(dustParticles.length>50){const oldDust=dustParticles.shift();oldDust.remove()}animateDust(dust)}function animateDust(dust){let opacity=1;let size=3;let posX=parseFloat(dust.style.left);let posY=parseFloat(dust.style.top);function updateDust(){opacity-=0.02;size-=0.05;posX+=(Math.random()-0.5)*2;posY-=0.5;if(opacity<=0||size<=0){dust.remove();return}dust.style.opacity=opacity;dust.style.width=`${size}px`;dust.style.height=`${size}px`;dust.style.left=`${posX}px`;dust.style.top=`${posY}px`;requestAnimationFrame(updateDust)}requestAnimationFrame(updateDust)}window.addEventListener("resize",()=>{const cacti=document.querySelectorAll(".cactus");cacti.forEach((cactus)=>{const bottomPercentage=parseFloat(cactus.style.bottom)/window.innerHeight*100;cactus.style.bottom=`${bottomPercentage}%`})})});",
    #         "language": "javascript"
    #     },
    #     {
    #         "filename": "index.html",
    #         "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Desert Landscape</title><style>body, html {height: 100%;margin: 0;padding: 0;overflow: hidden;}#desert {background: linear-gradient(gold, orange);width: 100%;height: 100%;position: relative;overflow: hidden;}.sand-dune {background: tan;border-radius: 50% 50% 0 0;width: 100%;height: 30%;position: absolute;bottom: 0;}#sun {background: tomato;border-radius: 50%;width: 100px;height: 100px;position: absolute;top: 10%;left: 10%;box-shadow: 0 0 50px tomato;}.cactus {background: #2e8b57;border-radius: 10px;width: 40px;transition: height 1s ease-out;position: absolute;bottom: 30%;}.cactus:before, .cactus:after {content: "";background: #2e8b57;border-radius: 10px;width: 20px;height: 30px;position: absolute;}.cactus:before {top: 30%;left: -15px;transform: rotate(45deg);}.cactus:after {top: 60%;right: -15px;transform: rotate(-45deg);}.dust {pointer-events: none;background: #d2b48cb3;border-radius: 50%;width: 3px;height: 3px;position: absolute;}</style></head><body><div id="desert"><div id="sun"></div><div class="sand-dune"></div></div><script src="/index.js"></script></body></html>",
    #         "language": "html"
    #     }
    # ],
    # "installation_commands": "null",
    # "additional_notes": "The code uses built-in libraries so no additional commands are required."
    # },
    # </example_answer_3>
    # """
    # return EXAMPLE_OUTPUTS


# to do: depreceate
# def get_games_examples() -> str:
#     indexjs_2048 = "const gameBoard=document.getElementById('game-board');const scoreElement=document.getElementById('score');const bestScoreElement=document.getElementById('best-score');const undoButton=document.getElementById('undo-btn');const newGameButton=document.getElementById('new-game-btn');const colorSelect=document.getElementById('color-select');let board=[];let score=0;let bestScore=0;let gameHistory=[];const colorSchemes={default:{2:'#eee4da',4:'#ede0c8',8:'#f2b179',16:'#f59563',32:'#f67c5f',64:'#f65e3b',128:'#edcf72',256:'#edcc61',512:'#edc850',1024:'#edc53f',2048:'#edc22e'},dark:{2:'#635B5B',4:'#7A6F6F',8:'#8F8383',16:'#A49797',32:'#B9ABAB',64:'#CEBFBF',128:'#E3D3D3',256:'#F8E7E7',512:'#FFFDFD',1024:'#FFFFFF',2048:'#FFF700'},pastel:{2:'#FFD1DC',4:'#FFB3BA',8:'#FFDFBA',16:'#FFFFBA',32:'#BAFFC9',64:'#BAE1FF',128:'#D0BAFF',256:'#F4BAFF',512:'#FFB3BA',1024:'#FFDFBA',2048:'#FFFFBA'}};function initializeGame(){board=Array(4).fill().map(()=>Array(4).fill(0));score=0;gameHistory=[];addNewTile();addNewTile();updateBoard();}function addNewTile(){const emptyTiles=[];for(let i=0;i<4;i++){for(let j=0;j<4;j++){if(board[i][j]===0){emptyTiles.push({row:i,col:j});}}}if(emptyTiles.length>0){const{row,col}=emptyTiles[Math.floor(Math.random()*emptyTiles.length)];board[row][col]=Math.random()<0.9?2:4;}}function updateBoard(){gameBoard.innerHTML='';for(let i=0;i<4;i++){for(let j=0;j<4;j++){const tile=document.createElement('div');tile.className='tile';tile.textContent=board[i][j]||'';if(board[i][j]!==0){const colorScheme=colorSchemes[colorSelect.value];tile.style.backgroundColor=colorScheme[board[i][j]]||'#3c3a32';tile.style.color=board[i][j]<=4?'#776e65':'#f9f6f2';}gameBoard.appendChild(tile);}}scoreElement.textContent=`Score: ${score}`;if(score>bestScore){bestScore=score;bestScoreElement.textContent=`Best: ${bestScore}`;}}function move(direction){gameHistory.push({board:JSON.parse(JSON.stringify(board)),score});let moved=false;const rotatedBoard=rotateBoard(direction);for(let i=0;i<4;i++){const row=rotatedBoard[i].filter(tile=>tile!==0);for(let j=0;j<row.length-1;j++){if(row[j]===row[j+1]){row[j]*=2;score+=row[j];row[j+1]=0;moved=true;}}const newRow=row.filter(tile=>tile!==0);while(newRow.length<4){newRow.push(0);}if(JSON.stringify(rotatedBoard[i])!==JSON.stringify(newRow)){moved=true;}rotatedBoard[i]=newRow;}board=rotateBoard(direction,true,rotatedBoard);if(moved){addNewTile();updateBoard();if(isGameOver()){alert('Game Over!');}else if(hasWon()){alert('Congratulations! You've reached 2048!');}}}function rotateBoard(direction,reverse=false,inputBoard=board){let rotatedBoard=JSON.parse(JSON.stringify(inputBoard));const transpose=()=>{for(let i=0;i<4;i++){for(let j=i;j<4;j++){[rotatedBoard[i][j],rotatedBoard[j][i]]=[rotatedBoard[j][i],rotatedBoard[i][j]];}}}; const reverse_rows=()=>{for(let i=0;i<4;i++){rotatedBoard[i].reverse();}};if(!reverse){if(direction==='up')transpose();if(direction==='right')reverse_rows();if(direction==='down'){transpose();reverse_rows();}}else{if(direction==='up')transpose();if(direction==='right')reverse_rows();if(direction==='down'){reverse_rows();transpose();}}return rotatedBoard;}function isGameOver(){for(let i=0;i<4;i++){for(let j=0;j<4;j++){if(board[i][j]===0)return false;if(i<3&&board[i][j]===board[i+1][j])return false;if(j<3&&board[i][j]===board[i][j+1])return false;}}return true;}function hasWon(){for(let i=0;i<4;i++){for(let j=0;j<4;j++){if(board[i][j]===2048)return true;}}return false;}function undo(){if(gameHistory.length>0){const lastState=gameHistory.pop();board=lastState.board;score=lastState.score;updateBoard();}}document.addEventListener('keydown',(e)=>{e.preventDefault();switch(e.key){case'ArrowUp':move('up');break;case'ArrowDown':move('down');break;case'ArrowLeft':move('left');break;case'ArrowRight':move('right');break;}});let touchStartX,touchStartY;gameBoard.addEventListener('touchstart',(e)=>{touchStartX=e.touches[0].clientX;touchStartY=e.touches[0].clientY;});gameBoard.addEventListener('touchend',(e)=>{if(!touchStartX||!touchStartY)return;const touchEndX=e.changedTouches[0].clientX;const touchEndY=e.changedTouches[0].clientY;const deltaX=touchEndX-touchStartX;const deltaY=touchEndY-touchStartY;if(Math.abs(deltaX)>Math.abs(deltaY)){if(deltaX>0){move('right');}else{move('left');}}else{if(deltaY>0){move('down');}else{move('up');}}touchStartX=null;touchStartY=null;});undoButton.addEventListener('click',undo);newGameButton.addEventListener('click',initializeGame);colorSelect.addEventListener('change',updateBoard);initializeGame();"
#     indexhtml_2048 = """<!DOCTYPE html><html lang="en"><head><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com; style-src 'unsafe-inline'; img-src data: blob: https://threejsfundamentals.org; connect-src 'none'; form-action 'none'; base-uri 'none';"><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>2048 Game</title><style>body{font-family:Arial,sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;background-color:#faf8ef}#game-container{text-align:center}#game-board{display:grid;grid-template-columns:repeat(4,1fr);grid-gap:15px;background-color:#bbada0;border-radius:5px;padding:15px;margin-bottom:20px}.tile{width:100px;height:100px;background-color:#cdc1b4;border-radius:3px;display:flex;justify-content:center;align-items:center;font-size:36px;font-weight:bold;color:#776e65;transition:all .1s ease-in-out}#score,#best-score{display:inline-block;padding:10px 20px;background-color:#bbada0;border-radius:3px;color:white;font-size:18px;margin:0 10px}#undo-btn,#new-game-btn{padding:10px 20px;font-size:18px;background-color:#8f7a66;color:white;border:none;border-radius:3px;cursor:pointer;margin:10px}#color-scheme{margin-top:20px}</style></head><body><div id="game-container"><div id="game-board"></div><div><span id="score">Score: 0</span><span id="best-score">Best: 0</span></div><button id="undo-btn">Undo</button><button id="new-game-btn">New Game</button><div id="color-scheme"><label for="color-select">Color Scheme:</label><select id="color-select"><option value="default">Default</option><option value="dark">Dark</option><option value="pastel">Pastel</option></select></div></div><script src="index.js"></script></body></html>"""

#     EXAMPLE_OUTPUTS = """
#         <example_question_1>:
#         Create a fully functional 2048 game with the following features:

#         -4x4 grid layout
#         -Smooth tile sliding and merging animations
#         -Score tracking and display
#         -Game over detection when no more moves are possible
#         -Win condition when 2048 tile is created
#         -Standard keyboard controls (arrow keys)
#         -Touch/swipe support for mobile devices
#         -Use only HTML, JavaScript, and CSS without any external dependencies, libraries, or frameworks.
#         -Generate all graphics within the code, avoiding reliance on external image files.
#         -Ensure the game runs in an HTML iframe without requiring any additional setup.
#         -Provide complete, runnable code without placeholders or omissions.
#         -Proactively address common bugs and pitfalls in 2048 game implementations.
#         -As the game will run in a self-contained HTML iframe, ensure that the code does not use any local or session storage.
#         -Ensure that any keystrokes used do not trigger the default browser behaviour. If the user uses arrow keys to play, it should not also trigger scrolling of the browser.

#         Include additional cool features that enhance the game experience, such as:
#         -Undo functionality
#         -Best score tracking
#         -Color scheme customization option
#         -Responsive design for various screen sizes

#         Prioritize code completeness, robustness, and readiness for immediate execution.
#         Structure the response as follows:
#         a. Brief introduction explaining the game and its features
#         b. HTML code (including inline CSS if applicable)
#         c. JavaScript code
#         d. Any additional CSS in a separate <style> tag or file
#         e. Instructions for running the game

#         Remember to focus on delivering a complete, functional, and engaging 2048 game implementation using web technologies that can be easily copied and pasted into an HTML file to run immediately in a web browser.

#         </example_question_1>:

#         <example_answer_1>
#         {{
#             "files": [
#                 {{
#                     "filename": "index.js",
#                     "content": "{indexjs_2048}",
#                     "language": "javascript",
#                 }},
#                 {{
#                     "filename": "index.html",
#                     "content": "{indexhtml_2048}",
#                     "language": "html",
#                 }}
#             ],
#             "installation_commands": "null",
#             "additional_notes": "The code uses built-in libraries so no additional commands are required."
#         }}
#         </example_answer_1>
#     """
#     return EXAMPLE_OUTPUTS


def _get_game_answer_examples() -> str:
    return """
        <example_input_1>
            Implement a fun, streamlined web game called 'Turbulent Skies' where players navigate an airplane through various weather conditions and obstacles.

            Features:
            - Create a scrolling background that simulates flying through the sky, with clouds moving from right to left.
            - Display an airplane sprite that the player can move up and down.
            - Allow the user to control the airplane with the arrow keys. Ensure that the movement is smooth and that the default key behaviour is disabled.
            - Generate random weather events (thunderstorms, clear skies, turbulence) that affect the airplane's movement. Create corresponding visual changes for the weather events.
            - Implement a 'turbulence meter' at the top of the screen that fills up as the plane encounters turbulence.
            - Add floating luggage items that appear randomly on the screen and move from right to left.
            - Display a score counter that increases when luggage items are collected.
            - Add a fuel gauge that depletes over time, requiring the player to collect fuel canisters to keep the plane flying.
            - Implement a 'game over' condition when the turbulence meter is full, or if the fuel gauge is empty, showing the final score and a 'Play Again' button.

            User Actions:
            1. Use the up and down arrow keys to move the airplane vertically, avoiding turbulence and collecting luggage.
            2. Press the spacebar to activate 'Smooth Air' mode, which temporarily reduces the effect of turbulence (can be used once every 30 seconds).
        </example_input_1>
        <example_output_1>
            {
            "files": [
                    {
                        "filename": "index.js",
                        "content": "const canvas=document.getElementById("gameCanvas");const ctx=canvas.getContext("2d");const turbulenceMeter=document.getElementById("turbulenceFill");const fuelGauge=document.getElementById("fuelFill");const scoreElement=document.getElementById("score");const gameOverScreen=document.getElementById("gameOver");const finalScoreElement=document.getElementById("finalScore");const playAgainButton=document.getElementById("playAgain");const smoothAirCooldownElement=document.getElementById("smoothAirCooldown");let canvasWidth=1600;let canvasHeight=900;let scale=1;function resizeCanvas(){const e=document.getElementById("gameContainer"),t=e.clientWidth,n=e.clientHeight;(scale=Math.min(t/canvasWidth,n/canvasHeight)),(canvas.width=canvasWidth*scale),(canvas.height=canvasHeight*scale),ctx.scale(scale,scale);}window.addEventListener("resize",resizeCanvas),resizeCanvas();const airplane={x:100,y:canvasHeight/2,width:100,height:50,speed:5,};const clouds=[];const luggageItems=[];const fuelCanisters=[];let turbulence=0;let fuel=100;let score=0;let gameOver=false;let smoothAirActive=false;let lastTime=0;let smoothAirTimer=0;const SMOOTH_AIR_DURATION=30000;const SMOOTH_AIR_COOLDOWN=30000;const weatherConditions=["clear","stormy","turbulent"];let currentWeather="clear";function createCloud(){return{x:canvasWidth,y:Math.random()*canvasHeight,width:100*Math.random()+50,height:50*Math.random()+25,speed:2*Math.random()+1,};}function createLuggage(){return{x:canvasWidth,y:Math.random()*canvasHeight,width:40,height:40,speed:3*Math.random()+2,};}function createFuel(){return{x:canvasWidth,y:Math.random()*canvasHeight,width:40,height:40,speed:3*Math.random()+2,};}function drawFuelCanisters(){ctx.fillStyle="#32CD32";fuelCanisters.forEach((e)=>{ctx.beginPath();ctx.arc(e.x,e.y,e.size,0,2*Math.PI);ctx.fill();});}function updateFuelCanisters(deltaTime){fuelCanisters.forEach((e)=>{e.x-=e.speed*deltaTime*60;if(e.x+e.size<0)e.x=canvasWidth;});if(Math.random()<0.002*deltaTime*60){fuelCanisters.push({x:canvasWidth,y:Math.random()*(canvasHeight-20),size:15,speed:3*Math.random()+2,});}}function drawAirplane(){ctx.fillStyle="#4A4A4A";ctx.beginPath();ctx.moveTo(airplane.x,airplane.y);ctx.lineTo(airplane.x+airplane.width,airplane.y+airplane.height/2);ctx.lineTo(airplane.x,airplane.y+airplane.height);ctx.closePath();ctx.fill();ctx.fillStyle="#C0C0C0";for(let i=0;i<3;i++){ctx.fillRect(airplane.x+5+20*i,airplane.y+15,15,10);}ctx.fillStyle="#4A4A4A";ctx.beginPath();ctx.moveTo(airplane.x+30,airplane.y+airplane.height-10);ctx.lineTo(airplane.x+20,airplane.y+airplane.height+20);ctx.lineTo(airplane.x+50,airplane.y+airplane.height-15);ctx.closePath();ctx.fill();}function drawCloud(cloud){ctx.fillStyle="rgba(255,255,255,0.8)";ctx.beginPath();ctx.arc(cloud.x,cloud.y,cloud.width/2,0,2*Math.PI);ctx.arc(cloud.x+cloud.width/4,cloud.y-cloud.height/4,cloud.width/3,0,2*Math.PI);ctx.arc(cloud.x+cloud.width/2,cloud.y,cloud.width/3,0,2*Math.PI);ctx.closePath();ctx.fill();}function drawLuggage(luggage){ctx.fillStyle="#8B4513";ctx.fillRect(luggage.x,luggage.y,luggage.width,luggage.height);ctx.fillStyle="#DAA520";ctx.fillRect(luggage.x+5,luggage.y+5,luggage.width-10,luggage.height-10);}function drawWeatherEffects(){if("stormy"===currentWeather){(ctx.fillStyle="rgba(0,0,0,0.3)"),ctx.fillRect(0,0,canvasWidth,canvasHeight);for(let e=0;e<50;e++){(ctx.strokeStyle="#FFFFFF"),ctx.beginPath();const t=Math.random()*canvasWidth,n=Math.random()*canvasHeight;ctx.moveTo(t,n),ctx.lineTo(t+10,n+10),ctx.stroke();}}else"turbulent"===currentWeather&&((ctx.fillStyle="rgba(255,165,0,0.2)"),ctx.fillRect(0,0,canvasWidth,canvasHeight));}function updateAirplane(deltaTime){if(keys.ArrowUp&&airplane.y>0){airplane.y-=airplane.speed*deltaTime*60;}if(keys.ArrowDown&&airplane.y<canvasHeight-airplane.height){airplane.y+=airplane.speed*deltaTime*60;}}function updateFuel(deltaTime){fuel-=0.05*deltaTime*60;if(fuel<=0){gameOver=true;showGameOver();}}function checkCollisions(){luggageItems.forEach((e,t)=>{e.x-=e.speed;if(e.x+e.width<0){luggageItems.splice(t,1);}if(airplane.x<e.x+e.width&&airplane.x+airplane.width>e.x&&airplane.y<e.y+e.height&&airplane.y+airplane.height>e.y){luggageItems.splice(t,1);score+=500;}});fuelCanisters.forEach((e)=>{if(airplane.x<e.x+e.size&&airplane.x+airplane.width>e.x-e.size&&airplane.y<e.y+e.size&&airplane.y+airplane.height>e.y-e.size){fuel=Math.min(fuel+20,100);e.x=canvasWidth;}});}function updateClouds(deltaTime){clouds.forEach((e)=>{e.x-=e.speed*deltaTime*60;if(e.x+e.width<0){e.x=canvasWidth;e.y=Math.random()*canvasHeight;}});}function updateTurbulence(deltaTime){if(currentWeather==="turbulent"&&!smoothAirActive){turbulence+=0.15*deltaTime*60;}else if(currentWeather==="stormy"&&!smoothAirActive){turbulence+=0.08*deltaTime*60;}else{turbulence=Math.max(0,turbulence-0.1*deltaTime*60);}if(turbulence>=100){gameOver=true;showGameOver();}}function updateWeather(deltaTime){if(Math.random()<0.003*deltaTime*60){currentWeather=weatherConditions[Math.floor(Math.random()*weatherConditions.length)];}}function updateSmoothAir(deltaTime){if(smoothAirActive){smoothAirTimer-=deltaTime*1000;if(smoothAirTimer<=0){smoothAirActive=false;smoothAirTimer=SMOOTH_AIR_COOLDOWN;}smoothAirCooldownElement.textContent=`Smooth Air Active for: ${Math.ceil(smoothAirTimer/1000)}s`;}else if(smoothAirTimer>0){smoothAirTimer-=deltaTime*1000;if(smoothAirTimer<=0){smoothAirCooldownElement.textContent="Smooth Air: Ready";}else{smoothAirCooldownElement.textContent=`Smooth Air Cooldown: ${Math.ceil(smoothAirTimer/1000)}s`;}}}function updateGame(deltaTime){updateAirplane(deltaTime);updateClouds(deltaTime);updateFuelCanisters(deltaTime);checkCollisions();updateTurbulence(deltaTime);updateFuel(deltaTime);updateWeather(deltaTime);updateSmoothAir(deltaTime);if(Math.random()<0.02*deltaTime*60){luggageItems.push(createLuggage());}if(Math.random()<0.01*deltaTime*60){fuelCanisters.push(createFuel());}}function drawGame(){ctx.clearRect(0,0,canvasWidth,canvasHeight);ctx.fillStyle="#87CEEB";ctx.fillRect(0,0,canvasWidth,canvasHeight);drawWeatherEffects();clouds.forEach(drawCloud);luggageItems.forEach(drawLuggage);drawFuelCanisters();drawAirplane();turbulenceMeter.style.width=`${turbulence}%`;fuelGauge.style.width=`${fuel}%`;scoreElement.textContent=`Score: ${Math.floor(score)}`;}function gameLoop(currentTime){if(lastTime===0){lastTime=currentTime;}const deltaTime=(currentTime-lastTime)/1000;lastTime=currentTime;if(!gameOver){updateGame(deltaTime);drawGame();}requestAnimationFrame(gameLoop);}function startGame(){airplane.y=canvasHeight/2;clouds.length=0;luggageItems.length=0;turbulence=0;fuel=100;score=0;gameOver=false;currentWeather="clear";smoothAirActive=false;lastTime=0;smoothAirTimer=0;for(let e=0;e<5;e++)clouds.push(createCloud());gameOverScreen.style.display="none";requestAnimationFrame(gameLoop);}function showGameOver(){finalScoreElement.textContent=Math.floor(score);gameOverScreen.style.display="block";}const keys={};playAgainButton.addEventListener("click",startGame);document.addEventListener("keydown",(e)=>{keys[e.code]=true;if(["ArrowUp","ArrowDown","Space"].includes(e.code)){e.preventDefault();}if(e.key===" "&&!smoothAirActive&&smoothAirTimer===0){smoothAirActive=true;smoothAirTimer=SMOOTH_AIR_DURATION;}});document.addEventListener("keyup",(e)=>{keys[e.code]=false;});startGame();",
                        "language": "javascript"
                    },
                    {
                        "filename": "index.html",
                        "content": "<!DOCTYPE html><html lang="en"><head><meta charset="utf-8" /><meta content="width=device-width, initial-scale=1.0" name="viewport" /><title>Turbulent Skies</title><style>body, html { margin: 0; padding: 0; height: 100%; overflow: hidden; font-family: Arial, sans-serif; } #gameContainer { position: relative; width: 100%; height: 0; padding-bottom: 56.25%; background-color: #7dc9e7; } #gameCanvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; } #turbulenceMeter { position: absolute; top: 10px; left: 10px; width: 200px; height: 20px; background-color: rgba(255, 255, 255, 0.5); border: 2px solid #333; } #turbulenceFill { width: 0%; height: 100%; background-color: #ff4500; } #score { position: absolute; top: 10px; right: 10px; color: white; font-size: 24px; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5); } #gameOver { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background-color: rgba(0, 0, 0, 0.7); color: white; padding: 20px; border-radius: 10px; text-align: center; display: none; } #playAgain { margin-top: 20px; padding: 10px 20px; font-size: 18px; cursor: pointer; } #smoothAirCooldown { position: absolute; bottom: 10px; left: 10px; color: white; font-size: 18px; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5); } #fuelGauge { position: absolute; top: 40px; left: 10px; width: 200px; height: 20px; background-color: rgba(255, 255, 255, 0.5); border: 2px solid #333; } #fuelFill { width: 100%; height: 100%; background-color: #32cd32; transition: width 0.3s; }</style></head><body><div id="gameContainer"><canvas id="gameCanvas"></canvas><div id="turbulenceMeter"><div id="turbulenceFill"></div></div><div id="fuelGauge"><div id="fuelFill"></div></div><div id="score">Score: 0</div><div id="smoothAirCooldown">Smooth Air: Ready</div><div id="gameOver"><h2>Game Over</h2><p>Your Score: <span id="finalScore"></span></p><button id="playAgain">Play Again</button></div></div><script src="index.js"></script></body></html>",
                        "language": "html"
                    }
                ]
            }
        </example_output_1>
        <example_input_2>
            Implement a web game of a police officer trying to catch a pickpocket in a crowded street scene.

            Features
            - Create a stable 2D city for the players and NPC to move through.
            - Multiple animated pedestrian figures moving smoothly around the city
            - One pedestrian figure representing the pickpocket, visually distinct
            - One police officer figure that can be smoothly controlled by the user using WASD keys. Ensure that the default keystroke behaviour is disabled.
            - Create a detection radius around the police officer. When the pickpocket enters this radius, highlight both the officer and pickpocket.
            - Add a score counter that increases when the police officer successfully catches the pickpocket (i.e. when they occupy the same space). After a catch, reset the pickpocket's position randomly on the screen.
            - Add a timer that counts down from 120 seconds. When the timer hits 0 seconds, display a "Game Over" screen that shows the final score, and allows the user to restart the game.

            User Actions:
            - use the WASD keys to control the policeman. Get close to the pickpocket to capture them and increase your score!
        </example_input_2>
        <example_output_2>
            {
            "files": [
                    {
                        "filename": "index.js",
                        "content": "const canvas=document.getElementById('gameCanvas');const ctx=canvas.getContext('2d');const scoreTimerElement=document.getElementById('scoreTimer');const gameOverScreen=document.getElementById('gameOverScreen');const finalScoreElement=document.getElementById('finalScore');const restartButton=document.getElementById('restartButton');let canvasWidth=1600;let canvasHeight=900;let scale=1;function resizeCanvas(){const container=document.getElementById('gameContainer');const containerWidth=container.clientWidth;const containerHeight=container.clientHeight;scale=Math.min(containerWidth/canvasWidth,containerHeight/canvasHeight);canvas.width=canvasWidth*scale;canvas.height=canvasHeight*scale;ctx.scale(scale,scale);}window.addEventListener('resize',resizeCanvas);resizeCanvas();const PEDESTRIAN_COUNT=30;const PEDESTRIAN_SIZE=30;const POLICE_SIZE=40;const PICKPOCKET_SIZE=35;const DETECTION_RADIUS=120;const GAME_DURATION=120;let score=0;let timeLeft=GAME_DURATION;let gameInterval;let timerInterval;let backgroundCanvas;class Character{constructor(x,y,size,color,speed){this.x=x;this.y=y;this.size=size;this.color=color;this.speed=speed;this.direction=Math.random()*Math.PI*2;}draw(){ctx.fillStyle=this.color;ctx.beginPath();ctx.arc(this.x,this.y,this.size/2,0,Math.PI*2);ctx.fill();}move(){this.x+=Math.cos(this.direction)*this.speed;this.y+=Math.sin(this.direction)*this.speed;this.x=(this.x+canvasWidth)%canvasWidth;this.y=(this.y+canvasHeight)%canvasHeight;if(Math.random()<0.02){this.direction=Math.random()*Math.PI*2;}}}class Police extends Character{constructor(x,y){super(x,y,POLICE_SIZE,'#1E90FF',6);this.movementX=0;this.movementY=0;}draw(){super.draw();ctx.fillStyle='#FFFFFF';ctx.beginPath();ctx.arc(this.x,this.y-7,7,0,Math.PI*2);ctx.fill();}move(){this.x+=this.movementX*this.speed;this.y+=this.movementY*this.speed;this.x=(this.x+canvasWidth)%canvasWidth;this.y=(this.y+canvasHeight)%canvasHeight;}}class Pickpocket extends Character{constructor(x,y){super(x,y,PICKPOCKET_SIZE,'#FF4500',4.5);this.normalColor='#FF4500';this.detectedColor='#FF69B4';}draw(){super.draw();ctx.fillStyle='#000000';ctx.beginPath();ctx.arc(this.x-7,this.y-7,4,0,Math.PI*2);ctx.arc(this.x+7,this.y-7,4,0,Math.PI*2);ctx.fill();}reset(){this.x=Math.random()*canvasWidth;this.y=Math.random()*canvasHeight;this.color=this.normalColor;this.direction=Math.random()*Math.PI*2;}}const police=new Police(canvasWidth/2,canvasHeight/2);const pickpocket=new Pickpocket(Math.random()*canvasWidth,Math.random()*canvasHeight);const pedestrians=[];for(let i=0;i<PEDESTRIAN_COUNT;i++){pedestrians.push(new Character(Math.random()*canvasWidth,Math.random()*canvasHeight,PEDESTRIAN_SIZE,`rgb(${Math.random()*200+55}, ${Math.random()*200+55}, ${Math.random()*200+55})`,4));}function createBackground(){backgroundCanvas=document.createElement('canvas');backgroundCanvas.width=canvasWidth;backgroundCanvas.height=canvasHeight;const bgCtx=backgroundCanvas.getContext('2d');bgCtx.fillStyle='#8B8B8B';bgCtx.fillRect(0,0,canvasWidth,canvasHeight);bgCtx.fillStyle='#555555';bgCtx.fillRect(0,canvasHeight/2-50,canvasWidth,100);bgCtx.fillRect(canvasWidth/2-50,0,100,canvasHeight);bgCtx.fillStyle='#A9A9A9';bgCtx.fillRect(0,canvasHeight/2-60,canvasWidth,10);bgCtx.fillRect(0,canvasHeight/2+50,canvasWidth,10);bgCtx.fillRect(canvasWidth/2-60,0,10,canvasHeight);bgCtx.fillRect(canvasWidth/2+50,0,10,canvasHeight);bgCtx.fillStyle='#FFFFFF';for(let i=0;i<canvasWidth;i+=40){bgCtx.fillRect(i,canvasHeight/2-30,20,60);}for(let i=0;i<canvasHeight;i+=40){bgCtx.fillRect(canvasWidth/2-30,i,60,20);}const buildingAreas=[{x:0,y:0,width:canvasWidth/2-60,height:canvasHeight/2-60},{x:canvasWidth/2+60,y:0,width:canvasWidth/2-60,height:canvasHeight/2-60},{x:0,y:canvasHeight/2+60,width:canvasWidth/2-60,height:canvasHeight/2-60},{x:canvasWidth/2+60,y:canvasHeight/2+60,width:canvasWidth/2-60,height:canvasHeight/2-60}];buildingAreas.forEach(area=>{for(let i=0;i<3;i++){for(let j=0;j<3;j++){bgCtx.fillStyle=`rgb(${Math.random()*100+100}, ${Math.random()*100+100}, ${Math.random()*100+100})`;const buildingWidth=area.width/3-20;const buildingHeight=area.height/3-20;bgCtx.fillRect(area.x+i*(area.width/3)+10,area.y+j*(area.height/3)+10,buildingWidth,buildingHeight);}}})}function drawBackground(){ctx.drawImage(backgroundCanvas,0,0);}function drawDetectionRadius(){ctx.strokeStyle='rgba(255, 255, 0, 0.3)';ctx.beginPath();ctx.arc(police.x,police.y,DETECTION_RADIUS,0,Math.PI*2);ctx.stroke();}function checkCollision(){const dx=police.x-pickpocket.x;const dy=police.y-pickpocket.y;const distance=Math.sqrt(dx*dx+dy*dy);if(distance<(POLICE_SIZE+PICKPOCKET_SIZE)/2){score++;pickpocket.reset();}if(distance<DETECTION_RADIUS){pickpocket.color=pickpocket.detectedColor;}else{pickpocket.color=pickpocket.normalColor;}}function updateScore(){scoreTimerElement.textContent=`Score: ${score} | Time: ${timeLeft}s`;}function gameLoop(){ctx.clearRect(0,0,canvasWidth,canvasHeight);drawBackground();drawDetectionRadius();pedestrians.forEach(pedestrian=>{pedestrian.move();pedestrian.draw();});police.move();police.draw();pickpocket.move();pickpocket.draw();checkCollision();updateScore();}function startGame(){score=0;timeLeft=GAME_DURATION;pickpocket.reset();gameOverScreen.style.display='none';createBackground();clearInterval(gameInterval);clearInterval(timerInterval);gameInterval=setInterval(gameLoop,1000/60);timerInterval=setInterval(()=>{timeLeft--;if(timeLeft<=0){endGame();}},1000);}function endGame(){clearInterval(gameInterval);clearInterval(timerInterval);finalScoreElement.textContent=score;gameOverScreen.style.display='block';}restartButton.addEventListener('click',startGame);const keys={};window.addEventListener('keydown',(e)=>{keys[e.key]=true;e.preventDefault();});window.addEventListener('keyup',(e)=>{keys[e.key]=false;e.preventDefault();});function updatePoliceMovement(){police.movementX=0;police.movementY=0;if(keys['ArrowUp']||keys['w'])police.movementY-=1;if(keys['ArrowDown']||keys['s'])police.movementY+=1;if(keys['ArrowLeft']||keys['a'])police.movementX-=1;if(keys['ArrowRight']||keys['d'])police.movementX+=1;if(police.movementX!==0&&police.movementY!==0){police.movementX*=Math.SQRT1_2;police.movementY*=Math.SQRT1_2;}}setInterval(updatePoliceMovement,1000/60);startGame();",
                        "language": "javascript"
                    },
                    {
                        "filename": "index.html",
                        "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Police Officer Catch the Pickpocket</title><style>body,html{margin:0;padding:0;height:100%;overflow:hidden;font-family:Arial,sans-serif}#gameContainer{position:relative;width:100%;height:0;padding-bottom:56.25%}#gameCanvas{position:absolute;top:0;left:0;width:100%;height:100%;background-color:#8B8B8B}#scoreTimer{position:absolute;top:10px;left:10px;color:white;font-size:18px;background-color:rgba(0,0,0,0.5);padding:5px 10px;border-radius:5px}#gameOverScreen{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background-color:rgba(0,0,0,0.8);color:white;padding:20px;border-radius:10px;text-align:center;display:none}#restartButton{margin-top:10px;padding:10px 20px;font-size:16px;cursor:pointer}</style></head><body><div id="gameContainer"><canvas id="gameCanvas"></canvas><div id="scoreTimer">Score: 0 | Time: 120s</div><div id="gameOverScreen"><h2>Game Over</h2><p>Final Score: <span id="finalScore"></span></p><button id="restartButton">Restart</button></div></div></body></html>",
                        "language": "html"
                    }
                ]
            }
        </example_output_2>
    """


def _get_game_question_examples() -> str:
    # depreceated rythmn game example
    #     <example_input_2>
    #     Generate a self-contained coding problem that requires the programmer to implement a fun, streamlined, hyper-casual web game with 3 user actions for the following persona: a longtime hip-hop enthusiast who used to attend live shows all the time.
    # </example_input_2>

    # <example_output_2>
    #     Implement a fun, streamlined web game called 'Rhythm Master' that challenges players to match beats and create their own hip-hop tracks.

    #     Features:
    #     -  Create a game board as 4x4 grid of colorful buttons. The game board should resemble a DJ's mixing panel.
    #     -  Use neon colors (e.g., hot pink, electric blue, lime green, and bright orange) for the buttons.
    #     -  Display a score counter at the top of the screen
    #     -  Show a 'Play' button to start the game and a 'Reset' button to restart
    #     -  Implement a timer that counts down from 60 seconds. When the timer ends, display a "Game Over" screen displaying the final score.
    #     -  Generate a random sequence of button highlights for the player to follow.
    #     -  The game should increase in difficulty as the player's score increases by speeding up the sequence and adding more buttons to remember.
    #     -  Provide distinct visual feedback for correct and incorrect button presses.
    #     -  Add visual effects like confetti when the player successfully completes a sequence

    #     User Actions:
    #     1. Click the 'Play' button to start the game and begin the countdown timer
    #     2. Click on the colorful buttons in the correct sequence to match the generated pattern
    #     3. Press the 'R' key to stop the current game and reset the score to zero
    # </example_output_2>
    return """
        <example_input_1>
            Generate a self-contained coding problem that requires the programmer to implement a fun, streamlined, hyper-casual web game with 1 user actions for the following persona: A police officer who is constantly trying to catch the pickpocket artist in the act.
        </example_input_1>

        <example_output_1>
            Implement a web game of a police officer trying to catch a pickpocket in a crowded street scene.

            Features
            - Create a stable 2D city for the players and NPC to move through.
            - Multiple animated pedestrian figures moving smoothly around the city
            - One pedestrian figure representing the pickpocket, visually distinct
            - One police officer figure that can be smoothly controlled by the user using WASD keys. Ensure that the default keystroke behaviour is disabled.
            - Create a detection radius around the police officer. When the pickpocket enters this radius, highlight both the officer and pickpocket.
            - Add a score counter that increases when the police officer successfully catches the pickpocket (i.e. when they occupy the same space). After a catch, reset the pickpocket's position randomly on the screen.
            - Add a timer that counts down from 120 seconds. When the timer hits 0 seconds, display a "Game Over" screen that shows the final score, and allows the user to restart the game.

            User Actions:
            - use the WASD keys to control the policeman. Get close to the pickpocket to capture them and increase your score!
        </example_output_1>

        <example_input_2>
            Generate a self-contained coding problem that requires the programmer to implement a fun, streamlined, hyper-casual web game with 2 user actions for the following persona: A middle-aged son who is a flight attendant, bonded with air travel stories.
        </example_input_2>
        <example_output_2>
            Implement a fun, streamlined web game called "Turbulent Skies" where players navigate an airplane through various weather conditions and obstacles.

            Features:
            - Create a scrolling background that simulates flying through the sky, with clouds moving from right to left.
            - Display an airplane sprite that the player can move up and down.
            - Allow the user to control the airplane with the arrow keys. Ensure that the movement is smooth and that the default key behaviour is disabled.
            - Generate random weather events (thunderstorms, clear skies, turbulence) that affect the airplane's movement. Create corresponding visual changes for the weather events.
            - Implement a 'turbulence meter' at the top of the screen that fills up as the plane encounters turbulence.
            - Add floating luggage items that appear randomly on the screen and move from right to left.
            - Display a score counter that increases when luggage items are collected.
            - Add a fuel gauge that depletes over time, requiring the player to collect fuel canisters to keep the plane flying.
            - Implement a 'game over' condition when the turbulence meter is full, or if the fuel gauge is empty, showing the final score and a "Play Again" button.

            User Actions:
            1. Use the up and down arrow keys to move the airplane vertically, avoiding turbulence and collecting luggage.
            2. Press the spacebar to activate "Smooth Air" mode, which temporarily reduces the effect of turbulence (can be used once every 30 seconds).
        </example_output_2>
    """


def _get_science_question_examples() -> str:
    return """
    <example_input_1>
        Generate a self-contained coding problem that requires the programmer to implement a streamlined science simulation with persona inspired visuals and content, with 2 user actions for the following persona: "A skeptical internet user who challenges researchers and their theories, demanding evidence for every claim".
    </example_input_1>

    <example_output_1>
        Create an interactive simulation of the Monty Hall problem to challenge skeptical users and demonstrate probability concepts.

        Features:
        - Create three closed doors displayed prominently on the screen.
        - Implement the Monty Hall problem logic: Place a prize behind one random door, allow the user to select a door, then reveal a non-winning door before giving the option to switch.
        - A scoreboard showing the number of wins and losses
        - A reset button to start a new game
        - Visual indicators for door selection and reveal (eg. a prize displayed behind the winning door, and a goat for the non-winning doors.)
        - A background of a corridor with relevant decorations.
        - Create a 'Run Simulation' button that automatically plays the game 1000 times, updating the scoreboard in real-time to show the win percentages for both 'staying' and 'switching' strategies, providing empirical evidence for skeptical users.at

        User Actions:
        1. Click on a door to reveal what is behind it, then decide wheter to switch or stay.
        2. Click on the 'Run Simulation' button to simulate the game 1000 times.
    </example_output_1>
    <example_input_2>
        Generate a self-contained coding problem that requires the programmer to implement a streamlined science simulation with persona inspired visuals and content, with 2 user actions for the following persona: "A renowned snooker historian specializing in the origins and development of the game".
    </example_input_2>
    <example_output_2>
        Implement an interactive 2D physics simulation of a simplified snooker table that demonstrates the principles of elastic collisions and momentum transfer. The simulation should have a historical aesthetic inspired by early 20th century snooker parlors.

        Features:
        - Create a 2D top-down view of a simplified rectangular snooker table with rounded corners.
        - Display 3 colored balls on the table: one white cue ball and two colored object balls.
        - The table should have a green baize texture and wooden rails with a vintage appearance.
        - Implement basic 2D physics for ball movement, including friction and collision detection.
        - When balls collide, they should behave according to the principles of elastic collision, transferring momentum realistically.
        - Add visual effects such as ball spin (represented by a rotating texture or pattern on the balls) and slight motion blur for moving balls.
        - Display a simple score counter in an antique-style web-safe font.
        - When a colored ball is pocketed (enters one of the table's corner pockets), increment the score counter. The simulation should continue running until manually reset by the user.
        - Remember to style all elements to fit the early 20th century snooker parlor aesthetic, using appropriate colors and textures to evoke a sense of the game's rich history.

       User Actions:
        1. Click and drag on the white cue ball to set its initial velocity vector. The direction and length of the drag should determine the direction and speed of the cue ball when released. A faint line should appear during the drag to indicate the projected path.
        2. Press the "R" key to reset the table, randomly positioning the colored balls while keeping the white cue ball in its starting position. This action should also reset the score counter to zero.
    </example_output_2>
    """


def _get_animation_question_examples() -> str:
    return """
        <example_input_1>
            Generate a self-contained coding problem that requires the programmer to implement a interactive visualization with persona inspired visuals and content, with 2 user actions for the following persona: "A high school music teacher who passionately believes in making music resources more accessible to society".
        </example_input_1>

        <example_output_1>
            "Create an interactive piano visualization using HTML, CSS, and JavaScript.

            Features:
            - User playable piano that should have 88 keys (52 white keys and 36 black keys). The user can play the piano by clicking on the piano keys.
            - When the user hovers over a key, it should visually highlight to indicate it can be played.
            - Clicking on a key should produce a pressing animation and play a corresponding piano note sound.
            - Implement a slider that adjusts the piano's volume, affecting the loudness of the notes played when keys are clicked.

            User Actions:
            1. Click on a piano key to play that note.
            2. Adjust the volume slider to increase or decrease the loudness of the piano.
        </example_output_1>
        <example_input_2>
            Generate a self-contained coding problem that requires the programmer to implement a interactive visualization with persona inspired visuals and content, with 3 user actions for the following persona: "An immunologist An immunologist studying the development of vaccines against infectious diseases".
        </example_input_2>
        <example_output_2>
            Create an interactive visualization of a vaccine molecular structure.

            Features:
            - Implement a 3D rotating model of a simplified vaccine molecule using HTML5 canvas and vanilla JavaScript. The molecule should consist of at least 10 interconnected atoms.
            - Each atom should be represented by a sphere, with connecting lines between atoms.
            - Color-code each atom based on type (e.g. red for oxygen, blue for nitrogen)
            - Implement a smooth rotation animation of the molecule
            - Allow users to click and drag the molecule to rotate it manually in any direction. The rotation should be smooth and responsive.
            - Include a slider control that adjusts the rotation speed of the automatic animation. The slider should range from completely stopped to rapid rotation.
            - Add hover functionality so that when a user hovers over an atom, a tooltip appears displaying information about that atom type (e.g. element name, atomic number, typical role in vaccines).

            User actions:
            1. Hover over an atom to view more information about the atom.
            2. Adjust the slider to control the rotation speed of the molecule animation.
            3. Click and drag the molecule to rotate it manually.
        </example_output_2>
        """


def _get_animation_answer_examples() -> str:
    return """
    <example_input_1>
        Create an interactive visualization of a vaccine molecular structure.

        Features:
        - Implement a 3D rotating model of a simplified vaccine molecule using HTML5 canvas and vanilla JavaScript. The molecule should consist of at least 10 interconnected atoms.
        - Each atom should be represented by a sphere, with connecting lines between atoms.
        - Color-code each atom based on type (e.g. red for oxygen, blue for nitrogen)
        - Implement a smooth rotation animation of the molecule
        - Allow users to click and drag the molecule to rotate it manually in any direction. The rotation should be smooth and responsive.
        - Include a slider control that adjusts the rotation speed of the automatic animation. The slider should range from completely stopped to rapid rotation.
        - Add hover functionality so that when a user hovers over an atom, a tooltip appears displaying information about that atom type (e.g. element name, atomic number, typical role in vaccines).

        User actions:
        1. Hover over an atom to view more information about the atom.
        2. Adjust the slider to control the rotation speed of the molecule animation.
        3. Click and drag the molecule to rotate it manually.
    </example_input_1>
    <example_output_1>
        {
        "files": [
            {
                "filename": "index.js",
                "content": "const canvas=document.getElementById("canvas");const ctx=canvas.getContext("2d");const speedSlider=document.getElementById("speedSlider");const tooltip=document.getElementById("tooltip");const atoms=[{x:0,y:0,z:0,radius:20,color:"#ff4136",element:"Oxygen",atomicNumber:8,role:"Forms hydrogen bonds in vaccine proteins"},{x:50,y:0,z:0,radius:25,color:"#0074d9",element:"Nitrogen",atomicNumber:7,role:"Essential component of amino acids in vaccine antigens"},{x:-50,y:0,z:0,radius:15,color:"#ffdc00",element:"Sulfur",atomicNumber:16,role:"Forms disulfide bonds in vaccine proteins"},{x:0,y:50,z:0,radius:30,color:"#2ecc40",element:"Carbon",atomicNumber:6,role:"Backbone of organic molecules in vaccines"},{x:0,y:-50,z:0,radius:18,color:"#ff851b",element:"Phosphorus",atomicNumber:15,role:"Part of nucleic acids in mRNA vaccines"},{x:0,y:0,z:50,radius:22,color:"#b10dc9",element:"Sodium",atomicNumber:11,role:"Electrolyte in vaccine formulations"},{x:0,y:0,z:-50,radius:28,color:"#f012be",element:"Potassium",atomicNumber:19,role:"Electrolyte in vaccine formulations"},{x:50,y:50,z:50,radius:17,color:"#aaaaaa",element:"Aluminum",atomicNumber:13,role:"Adjuvant in some vaccines"},{x:-50,y:-50,z:-50,radius:24,color:"#01ff70",element:"Magnesium",atomicNumber:12,role:"Cofactor for enzymes in vaccine production"},{x:-50,y:50,z:-50,radius:26,color:"#7fdbff",element:"Calcium",atomicNumber:20,role:"Stabilizer in vaccine formulations"}];let rotationX=0;let rotationY=0;let rotationZ=0;let isDragging=false;let lastMouseX,lastMouseY;let autoRotationSpeed=0.01;function drawMolecule(){ctx.clearRect(0,0,canvas.width,canvas.height);ctx.save();ctx.translate(canvas.width/2,canvas.height/2);const sortedAtoms=atoms.slice().sort((a,b)=>b.z-a.z);ctx.strokeStyle="#ccc";ctx.lineWidth=2;for(let i=0;i<atoms.length;i++){for(let j=i+1;j<atoms.length;j++){drawConnection(atoms[i],atoms[j]);}}sortedAtoms.forEach((atom)=>{const{x,y,z,radius,color}=rotatePoint(atom);const scale=200/(200-z);ctx.beginPath();ctx.arc(x*scale,y*scale,radius*scale,0,Math.PI*2);ctx.fillStyle=color;ctx.fill();ctx.strokeStyle="#000";ctx.stroke();});ctx.restore();}function drawConnection(atom1,atom2){const p1=rotatePoint(atom1);const p2=rotatePoint(atom2);ctx.beginPath();ctx.moveTo(p1.x,p1.y);ctx.lineTo(p2.x,p2.y);ctx.stroke();}function rotatePoint(point){let{x,y,z}=point;let temp=y;y=y*Math.cos(rotationX)-z*Math.sin(rotationX);z=temp*Math.sin(rotationX)+z*Math.cos(rotationX);temp=x;x=x*Math.cos(rotationY)+z*Math.sin(rotationY);z=-temp*Math.sin(rotationY)+z*Math.cos(rotationY);temp=x;x=x*Math.cos(rotationZ)-y*Math.sin(rotationZ);y=temp*Math.sin(rotationZ)+y*Math.cos(rotationZ);return{...point,x,y,z};}function animate(){if(!isDragging){rotationY+=autoRotationSpeed;}drawMolecule();requestAnimationFrame(animate);}canvas.addEventListener("mousedown",(e)=>{isDragging=true;lastMouseX=e.clientX;lastMouseY=e.clientY;});canvas.addEventListener("mousemove",(e)=>{if(isDragging){const deltaX=e.clientX-lastMouseX;const deltaY=e.clientY-lastMouseY;rotationY+=deltaX*0.01;rotationX+=deltaY*0.01;lastMouseX=e.clientX;lastMouseY=e.clientY;}const rect=canvas.getBoundingClientRect();const mouseX=e.clientX-rect.left;const mouseY=e.clientY-rect.top;handleHover(mouseX,mouseY);});canvas.addEventListener("mouseup",()=>{isDragging=false;});canvas.addEventListener("mouseleave",()=>{isDragging=false;tooltip.style.display="none";});speedSlider.addEventListener("input",(e)=>{autoRotationSpeed=e.target.value/5000;});function handleHover(mouseX,mouseY){const hoveredAtom=atoms.find((atom)=>{const{x,y,z,radius}=rotatePoint(atom);const scale=200/(200-z);const scaledX=x*scale+canvas.width/2;const scaledY=y*scale+canvas.height/2;const distance=Math.sqrt((mouseX-scaledX)**2+(mouseY-scaledY)**2);return distance<=radius*scale;});if(hoveredAtom){tooltip.style.display="block";tooltip.style.left=`${mouseX+10}px`;tooltip.style.top=`${mouseY+10}px`;tooltip.innerHTML=`<strong>${hoveredAtom.element}</strong><br>Atomic Number: ${hoveredAtom.atomicNumber}<br>Role: ${hoveredAtom.role}`;}else{tooltip.style.display="none";}}animate();const instructions=document.createElement("div");instructions.style.position="absolute";instructions.style.top="10px";instructions.style.left="10px";instructions.style.backgroundColor="rgba(255, 255, 255, 0.8)";instructions.style.padding="10px";instructions.style.borderRadius="5px";instructions.style.fontSize="14px";instructions.innerHTML=`<strong>Instructions:</strong><br>- Click and drag to rotate the molecule<br>- Use the slider to adjust rotation speed<br>- Hover over atoms for more information`;document.body.appendChild(instructions);",
                "language": "javascript"
            },
            {
                "filename": "index.html",
                "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><title>Vaccine Molecular Structure Visualization</title><style>body { margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f0f0f0; font-family: Arial, sans-serif; } #canvas { border: 1px solid #ccc; background-color: #fff; } #controls { position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); display: flex; align-items: center; background-color: rgba(255, 255, 255, 0.8); padding: 10px; border-radius: 5px; } #speedSlider { width: 200px; margin: 0 10px; } #tooltip { position: absolute; background-color: rgba(0, 0, 0, 0.8); color: white; padding: 5px 10px; border-radius: 3px; font-size: 12px; pointer-events: none; display: none; } </style></head><body><canvas id="canvas" width="800" height="600"></canvas><div id="controls"><span>Rotation Speed:</span><input type="range" id="speedSlider" min="0" max="100" value="50" /></div><div id="tooltip"></div><script src="index.js"></script></body></html>",
                "language": "html"
            }
            ]
        }
    </example_output_1>
    <example_input_2>
        Create an interactive visualization of a secure intelligence communication network. The visualization should feature the following visual elements:

        Features:
        - Implement a network of at least 5 interconnected nodes, with the central node being larger and brighter to represent the main intelligence asset.
        - Create an animation effect where the connecting lines pulse periodically, simulating active secure channels.
        - Glowing nodes representing intelligence assets, with a larger central node for the main asset
        - Pulsing lines connecting the nodes, representing secure communication channels
        - Occasional bursts of light traveling along the lines to simulate data transfer
        - Use a dark background representing a covert operations environment
        - Add a user interaction where clicking on any node causes a burst of light to travel from that node to all connected nodes, representing a data broadcast.
        - Implement a feature where hovering over a node displays a small pop-up with fictional agent codenames and their current status (e.g., 'Agent Raven: Active', 'Agent Falcon: Standby').

        User Actions:
        1. Click on any node to trigger a data broadcast
        2. Hover over any node to display an agent's current status.
    </example_input_2>
    <example_output_2>
        {
        "files": [
            {
                "filename": "index.js",
                "content": "const canvas = document.getElementById("canvas"); const ctx = canvas.getContext("2d"); const tooltip = document.getElementById("tooltip"); let width = (canvas.width = window.innerWidth); let height = (canvas.height = window.innerHeight); const nodes = [ { id: 0, x: 0, y: 0, radius: 20, color: "#00ffff", codename: "Agent Raven", status: "Active", }, { id: 1, x: 0, y: 0, radius: 10, color: "#00ff00", codename: "Agent Falcon", status: "Standby", }, { id: 2, x: 0, y: 0, radius: 10, color: "#ff00ff", codename: "Agent Eagle", status: "Active", }, { id: 3, x: 0, y: 0, radius: 10, color: "#ffff00", codename: "Agent Hawk", status: "Active", }, { id: 4, x: 0, y: 0, radius: 10, color: "#ff8000", codename: "Agent Owl", status: "Standby", }, ]; const edges = [ { source: 0, target: 1 }, { source: 0, target: 2 }, { source: 0, target: 3 }, { source: 0, target: 4 }, { source: 1, target: 2 }, { source: 2, target: 3 }, { source: 3, target: 4 }, { source: 4, target: 1 }, ]; function applyLayout() { const centerX = width / 2; const centerY = height / 2; const radius = Math.min(width, height) / 3; nodes.forEach((node, index) => { if (index === 0) { node.x = centerX; node.y = centerY; } else { const angle = ((index - 1) / (nodes.length - 1)) * Math.PI * 2; node.x = centerX + radius * Math.cos(angle); node.y = centerY + radius * Math.sin(angle); } }); } function drawNetwork() { ctx.clearRect(0, 0, width, height); edges.forEach((edge) => { const source = nodes[edge.source]; const target = nodes[edge.target]; ctx.beginPath(); ctx.moveTo(source.x, source.y); ctx.lineTo(target.x, target.y); ctx.strokeStyle = "rgba(255, 255, 255, 0.2)"; ctx.lineWidth = 2; ctx.stroke(); }); nodes.forEach((node) => { ctx.beginPath(); ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2); ctx.fillStyle = node.color; ctx.fill(); ctx.strokeStyle = "white"; ctx.lineWidth = 2; ctx.stroke(); }); } function pulsateEdges() { edges.forEach((edge) => { const source = nodes[edge.source]; const target = nodes[edge.target]; const dx = target.x - source.x; const dy = target.y - source.y; const dist = Math.sqrt(dx * dx + dy * dy); const normalizedDx = dx / dist; const normalizedDy = dy / dist; ctx.beginPath(); ctx.moveTo(source.x, source.y); ctx.lineTo(target.x, target.y); const gradient = ctx.createLinearGradient( source.x, source.y, target.x, target.y ); gradient.addColorStop(0, "rgba(255, 255, 255, 0.1)"); gradient.addColorStop(0.5, "rgba(255, 255, 255, 0.5)"); gradient.addColorStop(1, "rgba(255, 255, 255, 0.1)"); ctx.strokeStyle = gradient; ctx.lineWidth = 2; ctx.stroke(); const pulsePosition = (Date.now() % 2000) / 2000; const pulseX = source.x + dx * pulsePosition; const pulseY = source.y + dy * pulsePosition; ctx.beginPath(); ctx.arc(pulseX, pulseY, 3, 0, Math.PI * 2); ctx.fillStyle = "white"; ctx.fill(); }); } function animate() { drawNetwork(); pulsateEdges(); requestAnimationFrame(animate); } function handleClick(event) { const rect = canvas.getBoundingClientRect(); const mouseX = event.clientX - rect.left; const mouseY = event.clientY - rect.top; nodes.forEach((node) => { const dx = mouseX - node.x; const dy = mouseY - node.y; const distance = Math.sqrt(dx * dx + dy * dy); if (distance <= node.radius) { broadcastData(node); } }); } function broadcastData(sourceNode) { edges.forEach((edge) => { if (edge.source === sourceNode.id || edge.target === sourceNode.id) { const targetNode = nodes[edge.source === sourceNode.id ? edge.target : edge.source]; animateDataTransfer(sourceNode, targetNode); } }); } function animateDataTransfer(source, target) { const duration = 1000; const startTime = Date.now(); function animate() { const elapsed = Date.now() - startTime; const progress = Math.min(elapsed / duration, 1); const x = source.x + (target.x - source.x) * progress; const y = source.y + (target.y - source.y) * progress; ctx.beginPath(); ctx.arc(x, y, 5, 0, Math.PI * 2); ctx.fillStyle = "white"; ctx.fill(); if (progress < 1) { requestAnimationFrame(animate); } } animate(); } function handleMouseMove(event) { const rect = canvas.getBoundingClientRect(); const mouseX = event.clientX - rect.left; const mouseY = event.clientY - rect.top; let hoveredNode = null; nodes.forEach((node) => { const dx = mouseX - node.x; const dy = mouseY - node.y; const distance = Math.sqrt(dx * dx + dy * dy); if (distance <= node.radius) { hoveredNode = node; } }); if (hoveredNode) { tooltip.style.display = "block"; tooltip.style.left = `${event.clientX + 10}px`; tooltip.style.top = `${event.clientY + 10}px`; tooltip.textContent = `${hoveredNode.codename}: ${hoveredNode.status}`; } else { tooltip.style.display = "none"; } } function handleResize() { width = canvas.width = window.innerWidth; height = canvas.height = window.innerHeight; applyLayout(); } function init() { applyLayout(); animate(); canvas.addEventListener("click", handleClick); canvas.addEventListener("mousemove", handleMouseMove); window.addEventListener("resize", handleResize); } init(); const instructions = document.createElement("div"); instructions.style.position = "absolute"; instructions.style.bottom = "10px"; instructions.style.left = "10px"; instructions.style.color = "white"; instructions.style.fontSize = "14px"; instructions.innerHTML = "Click on a node to broadcast data. Hover over nodes to see agent information."; document.body.appendChild(instructions);",
                "language": "javascript"
            },
            {
                "filename": "index.html",
                "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><title>Secure Intelligence Communication Network</title><style>body{margin:0;overflow:hidden;background-color:#000;font-family:Arial,sans-serif}#canvas{display:block}#tooltip{position:absolute;background-color:rgba(0,0,0,0.8);color:#fff;padding:5px;border-radius:5px;display:none}</style></head><body><canvas id="canvas"></canvas><div id="tooltip"></div><script src="index.js"></script></body></html>",
                "language": "html"
            }
            ]
        }
    </example_output_2>
    """


def _get_science_answer_examples() -> str:
    return """
    <example_input_1>
        Create an interactive golf ball trajectory simulator that models the physics of a golf ball's flight, incorporating factors like wind speed and direction.

        Features:
        - A 2D side-view golf course display with a tee area, fairway, and green
        - A movable golfer figure at the tee
        - A golf ball that follows a realistic trajectory when hit
        - Wind direction indicator (e.g. an arrow)
        - Wind speed display
        - Distance markers along the fairway
        - A trajectory path line that shows the ball's flight
        - A landing spot indicator
        - A scoreboard displaying current shot distance and best distance
        - When the user has set their desired parameters, they should be able to initiate the shot with a 'Swing' button. The ball should then follow a realistic trajectory based on the input parameters and wind conditions, with the path visually traced on the screen. After the ball lands, update the scoreboard with the shot distance and best distance if applicable.

        User Actions:
        1. Adjust Shot Power: Allow the user to set the initial velocity of the golf ball by clicking and dragging a power meter or using a slider. The power should be visually represented, perhaps by the backswing of the golfer figure.
        2. Set Shot Angle: Enable the user to change the launch angle of the shot by clicking and dragging the golfer figure or using arrow keys. The angle should be displayed numerically and visually represented by the golfer's stance.
        3. Control Wind Conditions: Implement a way for users to adjust wind speed and direction, such as with sliders or by clicking and dragging a wind indicator. The wind arrow should update in real-time to reflect these changes.
    </example_input_1>
    <example_output_1>
        {
        "files": [
                {
                    "filename": "index.js",
                    "content": "const canvas=document.getElementById("canvas");const ctx=canvas.getContext("2d");const container=document.getElementById("canvas-container");let scale;const baseWidth=1600;const baseHeight=900;function resizeCanvas(){const containerWidth=container.clientWidth;const containerHeight=container.clientHeight;const containerRatio=containerWidth/containerHeight;const gameRatio=16/9;if(containerRatio>gameRatio){canvas.height=containerHeight;canvas.width=containerHeight*gameRatio;}else{canvas.width=containerWidth;canvas.height=containerWidth/gameRatio;}scale=canvas.width/baseWidth;}resizeCanvas();window.addEventListener("resize",resizeCanvas);const powerSlider=document.getElementById("powerSlider");const angleSlider=document.getElementById("angleSlider");const windSpeedSlider=document.getElementById("windSpeedSlider");const windDirectionSlider=document.getElementById("windDirectionSlider");const swingButton=document.getElementById("swingButton");const currentDistanceSpan=document.getElementById("currentDistance");const bestDistanceSpan=document.getElementById("bestDistance");const windIndicatorDiv=document.getElementById("windIndicator");let bestDistance=0;let ballInFlight=false;let ballPosition={x:100,y:baseHeight-80};let ballVelocity={x:0,y:0};let time=0;const flagPosition=450*3+100;function drawCourse(){ctx.fillStyle="#87CEEB";ctx.fillRect(0,0,canvas.width,canvas.height);ctx.fillStyle="#228B22";ctx.fillRect(0,canvas.height-80*scale,canvas.width,80*scale);ctx.fillStyle="#8B4513";ctx.fillRect(80*scale,canvas.height-85*scale,40*scale,5*scale);ctx.fillStyle="white";ctx.font=`${14*scale}px Arial`;for(let i=100;i<=500;i+=100){let x=i*3*scale;ctx.fillText(`${i}m`,x,canvas.height-90*scale);ctx.fillRect(x,canvas.height-80*scale,2*scale,10*scale);}drawFlag();}function drawFlag(){ctx.strokeStyle="#000000";ctx.lineWidth=2*scale;ctx.beginPath();ctx.moveTo(flagPosition*scale,canvas.height-80*scale);ctx.lineTo(flagPosition*scale,canvas.height-160*scale);ctx.stroke();ctx.fillStyle="#FF0000";ctx.beginPath();ctx.moveTo(flagPosition*scale,canvas.height-160*scale);ctx.lineTo((flagPosition+30)*scale,canvas.height-145*scale);ctx.lineTo(flagPosition*scale,canvas.height-130*scale);ctx.closePath();ctx.fill();ctx.fillStyle="#000000";ctx.beginPath();ctx.arc(flagPosition*scale,canvas.height-80*scale,5*scale,0,Math.PI*2);ctx.fill();}function drawGolfer(){ctx.fillStyle="black";ctx.beginPath();ctx.arc(100*scale,canvas.height-100*scale,10*scale,0,Math.PI*2);ctx.fill();let angle=(angleSlider.value*Math.PI)/180;ctx.beginPath();ctx.moveTo(100*scale,canvas.height-100*scale);ctx.lineTo(100*scale+Math.cos(angle)*30*scale,canvas.height-100*scale-Math.sin(angle)*30*scale);ctx.lineWidth=3*scale;ctx.stroke();}function drawBall(){ctx.fillStyle="white";ctx.beginPath();ctx.arc(ballPosition.x*scale,ballPosition.y*scale,5*scale,0,Math.PI*2);ctx.fill();}function drawWindIndicator(){let windSpeed=windSpeedSlider.value;let windDirection=(windDirectionSlider.value*Math.PI)/180;const windCanvas=document.createElement("canvas");windCanvas.width=40;windCanvas.height=40;const windCtx=windCanvas.getContext("2d");windCtx.save();windCtx.translate(20,20);windCtx.rotate(windDirection);windCtx.fillStyle="black";windCtx.beginPath();windCtx.moveTo(0,-15);windCtx.lineTo(5,-10);windCtx.lineTo(2,-10);windCtx.lineTo(2,15);windCtx.lineTo(-2,15);windCtx.lineTo(-2,-10);windCtx.lineTo(-5,-10);windCtx.closePath();windCtx.fill();windCtx.restore();windCtx.fillStyle="black";windCtx.font="10px Arial";windCtx.textAlign="center";windCtx.textBaseline="middle";windCtx.fillText(`${windSpeed}`,20,35);windIndicatorDiv.innerHTML="";windIndicatorDiv.appendChild(windCanvas);}function updateBallPosition(){if(!ballInFlight)return;let g=9.81;let dt=0.1;let windSpeed=windSpeedSlider.value;let windDirection=(windDirectionSlider.value*Math.PI)/180;let windScaleFactor=0.05;let windForce={x:windSpeed*Math.cos(windDirection)*windScaleFactor,y:windSpeed*Math.sin(windDirection)*windScaleFactor,};ballVelocity.x+=windForce.x*dt;ballVelocity.y+=windForce.y*dt;ballVelocity.y-=g*dt;ballPosition.x+=ballVelocity.x*dt;ballPosition.y-=ballVelocity.y*dt;if(ballPosition.y>=baseHeight-80){ballInFlight=false;let distance=Math.round((ballPosition.x-100)/3);currentDistanceSpan.textContent=distance;if(distance>bestDistance){bestDistance=distance;bestDistanceSpan.textContent=bestDistance;}}time+=dt;}function drawTrajectory(){if(!ballInFlight)return;ctx.strokeStyle="rgba(255, 0, 0, 0.3)";ctx.lineWidth=2*scale;ctx.beginPath();ctx.moveTo(100*scale,canvas.height-80*scale);ctx.lineTo(ballPosition.x*scale,ballPosition.y*scale);ctx.stroke();}function swing(){let power=powerSlider.value*0.5;let angle=(angleSlider.value*Math.PI)/180;ballPosition={x:100,y:baseHeight-80};ballVelocity={x:power*Math.cos(angle),y:power*Math.sin(angle),};time=0;ballInFlight=true;}function animate(){ctx.clearRect(0,0,canvas.width,canvas.height);drawCourse();drawWindIndicator();drawGolfer();updateBallPosition();drawTrajectory();drawBall();requestAnimationFrame(animate);}swingButton.addEventListener("click",swing);animate();window.addEventListener("resize",()=>{resizeCanvas();ballPosition={x:100,y:baseHeight-80};});",
                    "language": "javascript"
                },
                {
                    "filename": "index.html",
                    "content": "<!DOCTYPE html><html lang="en"><head><meta charset="utf-8" /><meta content="width=device-width, initial-scale=1.0" name="viewport" /><title>Golf Ball Trajectory Simulator</title><style>body,html{margin:0;padding:0;overflow:hidden;font-family:Arial,sans-serif;width:100%;height:100%}#canvas-container{width:100%;height:100%;display:flex;justify-content:center;align-items:center;background-color:#f0f0f0}#canvas{max-width:100%;max-height:100%}#controls{position:absolute;top:10px;left:10px;background:rgba(255,255,255,0.7);padding:5px;border-radius:3px;display:flex;flex-direction:column;gap:5px;font-size:12px}#controls input[type="range"]{width:80px;margin:0}#controls label{display:flex;justify-content:space-between;align-items:center}#swingButton{margin-top:5px;padding:2px 5px;font-size:12px}#scoreboard{position:absolute;top:10px;right:10px;background:rgba(255,255,255,0.7);padding:5px;border-radius:3px;font-size:12px}#windIndicator{width:40px;height:40px;align-self:center}#scoreboard p{margin:2px 0}</style></head><body><div id="canvas-container"><canvas id="canvas"></canvas></div><div id="controls"><label>Power:<input id="powerSlider" max="100" min="0" type="range" value="50"/></label><label>Angle:<input id="angleSlider" max="90" min="0" type="range" value="45"/></label><label>Wind Speed:<input id="windSpeedSlider" max="20" min="0" type="range" value="0"/></label><label>Wind Dir:<input id="windDirectionSlider" max="360" min="0" type="range" value="0"/></label><div id="windIndicator"></div><button id="swingButton">Swing</button></div><div id="scoreboard"><p>Current: <span id="currentDistance">0</span> m</p><p>Best: <span id="bestDistance">0</span> m</p></div><script src="index.js"></script></body></html>",
                    "language": "html"
                }
            ]
        }
    </example_output_1>
    <example_input_2>
        Implement an interactive 2D physics simulation of a simplified snooker table that demonstrates the principles of elastic collisions and momentum transfer. The simulation should have a historical aesthetic inspired by early 20th century snooker parlors.

        Features:
        - Create a 2D top-down view of a simplified rectangular snooker table with rounded corners.
        - Display 3 colored balls on the table: one white cue ball and two colored object balls.
        - The table should have a green baize texture and wooden rails with a vintage appearance.
        - Implement basic 2D physics for ball movement, including friction and collision detection.
        - When balls collide, they should behave according to the principles of elastic collision, transferring momentum realistically.
        - Add visual effects such as ball spin (represented by a rotating texture or pattern on the balls) and slight motion blur for moving balls.
        - Display a simple score counter in an antique-style web-safe font.
        - When a colored ball is pocketed (enters one of the table's corner pockets), increment the score counter. The simulation should continue running until manually reset by the user.
        - Remember to style all elements to fit the early 20th century snooker parlor aesthetic, using appropriate colors and textures to evoke a sense of the game's rich history.

       User Actions:
        1. Click and drag on the white cue ball to set its initial velocity vector. The direction and length of the drag should determine the direction and speed of the cue ball when released. A faint line should appear during the drag to indicate the projected path.
        2. Press the "R" key to reset the table, randomly positioning the colored balls while keeping the white cue ball in its starting position. This action should also reset the score counter to zero.
    </example_input_2>
    <example_output_2>
        {
        "files": [
                {
                    "filename": "index.js",
                    "content": "const gameContainer=document.getElementById("gameContainer");const canvas=document.getElementById("snookerCanvas");const ctx=canvas.getContext("2d");const scoreCounter=document.getElementById("scoreCounter");let TABLE_WIDTH,TABLE_HEIGHT,BALL_RADIUS,POCKET_RADIUS;const FRICTION=0.99;const COLLISION_DAMPING=0.9;let balls=[];let score=0;let isDragging=false;let dragStart={x:0,y:0};let dragEnd={x:0,y:0};function resizeCanvas(){canvas.width=gameContainer.clientWidth;canvas.height=gameContainer.clientHeight;TABLE_WIDTH=canvas.width;TABLE_HEIGHT=canvas.height;BALL_RADIUS=Math.min(TABLE_WIDTH,TABLE_HEIGHT)*0.025;POCKET_RADIUS=BALL_RADIUS*1.5;initializeBalls()}class Ball{constructor(x,y,color){this.x=x;this.y=y;this.vx=0;this.vy=0;this.color=color;this.rotation=0}draw(){ctx.save();ctx.translate(this.x,this.y);ctx.rotate(this.rotation);ctx.beginPath();ctx.arc(0,0,BALL_RADIUS,0,Math.PI*2);ctx.fillStyle=this.color;ctx.fill();ctx.strokeStyle="black";ctx.lineWidth=BALL_RADIUS*0.1;ctx.stroke();ctx.beginPath();ctx.moveTo(0,-BALL_RADIUS);ctx.lineTo(0,BALL_RADIUS);ctx.strokeStyle="rgba(0,0,0,0.3)";ctx.lineWidth=BALL_RADIUS*0.1;ctx.stroke();ctx.restore()}update(){this.x+=this.vx;this.y+=this.vy;this.vx*=FRICTION;this.vy*=FRICTION;this.rotation+=Math.sqrt(this.vx*this.vx+this.vy*this.vy)*0.05;if(this.x-BALL_RADIUS<0||this.x+BALL_RADIUS>TABLE_WIDTH){this.vx*=-1}if(this.y-BALL_RADIUS<0||this.y+BALL_RADIUS>TABLE_HEIGHT){this.vy*=-1}}}function initializeBalls(){balls=[new Ball(TABLE_WIDTH/4,TABLE_HEIGHT/2,"white"),new Ball((TABLE_WIDTH*3)/4,TABLE_HEIGHT/2-TABLE_HEIGHT/12,"red"),new Ball((TABLE_WIDTH*3)/4,TABLE_HEIGHT/2+TABLE_HEIGHT/12,"black")]}function drawTable(){ctx.fillStyle="#0a5c0a";ctx.fillRect(0,0,TABLE_WIDTH,TABLE_HEIGHT);ctx.strokeStyle="#43290a";ctx.lineWidth=TABLE_WIDTH*0.02;ctx.strokeRect(0,0,TABLE_WIDTH,TABLE_HEIGHT);const pockets=[{x:0,y:0},{x:TABLE_WIDTH,y:0},{x:0,y:TABLE_HEIGHT},{x:TABLE_WIDTH,y:TABLE_HEIGHT},{x:TABLE_WIDTH/2,y:0},{x:TABLE_WIDTH/2,y:TABLE_HEIGHT}];pockets.forEach((pocket)=>{ctx.beginPath();ctx.arc(pocket.x,pocket.y,POCKET_RADIUS,0,Math.PI*2);ctx.fillStyle="black";ctx.fill()})}function drawProjectionLine(){if(isDragging){ctx.beginPath();ctx.moveTo(dragStart.x,dragStart.y);ctx.lineTo(dragEnd.x,dragEnd.y);ctx.strokeStyle="rgba(255,255,255,0.5)";ctx.lineWidth=BALL_RADIUS*0.2;ctx.stroke()}}function checkCollisions(){for(let i=0;i<balls.length;i++){for(let j=i+1;j<balls.length;j++){const dx=balls[j].x-balls[i].x;const dy=balls[j].y-balls[i].y;const distance=Math.sqrt(dx*dx+dy*dy);if(distance<BALL_RADIUS*2){const angle=Math.atan2(dy,dx);const sin=Math.sin(angle);const cos=Math.cos(angle);const vx1=balls[i].vx*cos+balls[i].vy*sin;const vy1=balls[i].vy*cos-balls[i].vx*sin;const vx2=balls[j].vx*cos+balls[j].vy*sin;const vy2=balls[j].vy*cos-balls[j].vx*sin;const finalVx1=vx2;const finalVx2=vx1;balls[i].vx=(finalVx1*cos-vy1*sin)*COLLISION_DAMPING;balls[i].vy=(vy1*cos+finalVx1*sin)*COLLISION_DAMPING;balls[j].vx=(finalVx2*cos-vy2*sin)*COLLISION_DAMPING;balls[j].vy=(vy2*cos+finalVx2*sin)*COLLISION_DAMPING;const overlap=2*BALL_RADIUS-distance;balls[i].x-=(overlap/2)*cos;balls[i].y-=(overlap/2)*sin;balls[j].x+=(overlap/2)*cos;balls[j].y+=(overlap/2)*sin}}}}function checkPockets(){const pockets=[{x:0,y:0},{x:TABLE_WIDTH,y:0},{x:0,y:TABLE_HEIGHT},{x:TABLE_WIDTH,y:TABLE_HEIGHT},{x:TABLE_WIDTH/2,y:0},{x:TABLE_WIDTH/2,y:TABLE_HEIGHT}];for(let i=balls.length-1;i>=0;i--){for(const pocket of pockets){const dx=balls[i].x-pocket.x;const dy=balls[i].y-pocket.y;const distance=Math.sqrt(dx*dx+dy*dy);if(distance<POCKET_RADIUS){if(balls[i].color!=="white"){score++;scoreCounter.textContent=`Score:${score}`;balls.splice(i,1)}else{balls[i].x=TABLE_WIDTH/4;balls[i].y=TABLE_HEIGHT/2;balls[i].vx=0;balls[i].vy=0}break}}}}function gameLoop(){ctx.clearRect(0,0,TABLE_WIDTH,TABLE_HEIGHT);drawTable();drawProjectionLine();balls.forEach((ball)=>{ball.update();ball.draw()});checkCollisions();checkPockets();requestAnimationFrame(gameLoop)}function resetGame(){initializeBalls();score=0;scoreCounter.textContent=`Score:${score}`}canvas.addEventListener("mousedown",(e)=>{const rect=canvas.getBoundingClientRect();const mouseX=(e.clientX-rect.left)*(canvas.width/rect.width);const mouseY=(e.clientY-rect.top)*(canvas.height/rect.height);if(Math.abs(mouseX-balls[0].x)<BALL_RADIUS&&Math.abs(mouseY-balls[0].y)<BALL_RADIUS){isDragging=true;dragStart={x:mouseX,y:mouseY}}});canvas.addEventListener("mousemove",(e)=>{if(isDragging){const rect=canvas.getBoundingClientRect();dragEnd={x:(e.clientX-rect.left)*(canvas.width/rect.width),y:(e.clientY-rect.top)*(canvas.height/rect.height)}}});canvas.addEventListener("mouseup",()=>{if(isDragging){const dx=dragStart.x-dragEnd.x;const dy=dragStart.y-dragEnd.y;const speed=Math.sqrt(dx*dx+dy*dy)*0.1;balls[0].vx=dx*speed*0.01;balls[0].vy=dy*speed*0.01;isDragging=false}});document.addEventListener("keydown",(e)=>{if(e.key.toLowerCase()==="r"){resetGame()}});window.addEventListener("resize",resizeCanvas);resizeCanvas();gameLoop();",
                    "language": "javascript"
                },
                {
                    "filename": "index.html",
                    "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><title>Snooker Through the Ages</title><style>body,html{margin:0;padding:0;width:100%;height:100%;overflow:hidden;background-color:#2c1c0f;font-family:Georgia,serif}#gameContainer{position:relative;width:100%;height:0;padding-bottom:56.25%;background-color:#1a0f07;border:10px solid #43290a;box-sizing:border-box}#banner{position:absolute;top:2%;left:50%;transform:translateX(-50%);font-size:3vw;color:#d4af37;text-shadow:2px 2px 4px rgba(0,0,0,0.5);white-space:nowrap}#scoreCounter{position:absolute;bottom:2%;left:50%;transform:translateX(-50%);font-size:2vw;color:#d4af37}#snookerCanvas{position:absolute;top:0;left:0;width:100%;height:100%}</style></head><body><div id="gameContainer"><div id="banner">Snooker Through the Ages</div><canvas id="snookerCanvas"></canvas><div id="scoreCounter">Score: 0</div></div><script src="index.js"></script></body></html>",
                    "language": "html"
                }
            ]
        }
    </example_output_2>
    """
