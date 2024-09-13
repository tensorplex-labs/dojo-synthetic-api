def few_shot_example_outputs() -> str:
    EXAMPLE_OUTPUTS = """
    <example_question_1>:
    "Create a Solar System Orbit Simulator using JavaScript, HTML, and CSS. The simulator should display the Sun at the center of the screen and at least 4 planets orbiting around it.
        Requirements:
        1. Implement a slider that controls the speed of the planets' orbits. The slider should allow users to adjust the simulation speed from very slow to very fast.

        2. Add a feature that allows users to click on a planet to display its name and basic information (e.g., size, distance from the Sun) in a small pop-up or sidebar.

        3. Include a button that toggles the visibility of planet orbit paths. When enabled, it should show the elliptical paths of the planets' orbits.

        Ensure that the planets' sizes and distances are proportional (though not necessarily to scale) to represent the relative differences in the solar system. Use only built-in JavaScript libraries and features for this implementation.
        Note:
        - The visualization should be implemented in JavaScript with HTML and CSS.
        - Ensure that the output has both index.js and index.html files",
    </example_question_1>:

    <example_answer_1>
    {
        "files": [
            {
                "filename": "index.js",
                "content": "const canvas=document.getElementById("canvas");const ctx=canvas.getContext("2d");const speedSlider=document.getElementById("speed");const toggleOrbitsBtn=document.getElementById("toggleOrbits");const infoDiv=document.getElementById("info");let width=(canvas.width=window.innerWidth);let height=(canvas.height=window.innerHeight);let centerX=width/2;let centerY=height/2;let showOrbits=false;const planets=[{name:"Mercury",color:"#8c7e6d",radius:5,distance:60,speed:0.04,angle:0,info:"Smallest planet, closest to Sun"},{name:"Venus",color:"#e3bb76",radius:8,distance:100,speed:0.015,angle:0,info:"Hottest planet, rotates backwards"},{name:"Earth",color:"#4f94cd",radius:9,distance:150,speed:0.01,angle:0,info:"Our home planet, supports life"},{name:"Mars",color:"#c1440e",radius:7,distance:200,speed:0.008,angle:0,info:"The Red Planet, has polar ice caps"}];function drawSun(){ctx.beginPath();ctx.arc(centerX,centerY,20,0,Math.PI*2);ctx.fillStyle="#ffd700";ctx.fill();}function drawPlanet(planet){const x=centerX+Math.cos(planet.angle)*planet.distance;const y=centerY+Math.sin(planet.angle)*planet.distance;if(showOrbits){ctx.beginPath();ctx.arc(centerX,centerY,planet.distance,0,Math.PI*2);ctx.strokeStyle="rgba(255, 255, 255, 0.2)";ctx.stroke();}ctx.beginPath();ctx.arc(x,y,planet.radius,0,Math.PI*2);ctx.fillStyle=planet.color;ctx.fill();}function updatePlanets(){const speed=parseFloat(speedSlider.value);planets.forEach((planet)=>{planet.angle+=planet.speed*speed;});}let stars=[];function initStars(){stars=[];for(let i=0;i<200;i++){stars.push({x:Math.random()*width,y:Math.random()*height,size:Math.random()*1.5,speed:Math.random()*0.08+0.01});}}function drawStars(){ctx.fillStyle="#ffffff";for(const star of stars){ctx.beginPath();ctx.arc(star.x,star.y,star.size,0,Math.PI*2);ctx.fill();star.y+=star.speed;if(star.y>height){star.y=0;star.x=Math.random()*width;}}}function animate(){ctx.clearRect(0,0,width,height);drawStars();drawSun();planets.forEach(drawPlanet);updatePlanets();requestAnimationFrame(animate);}function handleResize(){width=canvas.width=window.innerWidth;height=canvas.height=window.innerHeight;centerX=width/2;centerY=height/2;initStars();}function showPlanetInfo(event){const rect=canvas.getBoundingClientRect();const mouseX=event.clientX-rect.left;const mouseY=event.clientY-rect.top;for(const planet of planets){const planetX=centerX+Math.cos(planet.angle)*planet.distance;const planetY=centerY+Math.sin(planet.angle)*planet.distance;const distance=Math.sqrt((mouseX-planetX)**2+(mouseY-planetY)**2);if(distance<=planet.radius){infoDiv.innerHTML=`<h3>${planet.name}</h3><p>${planet.info}</p>`;infoDiv.style.display="block";return;}}infoDiv.style.display="none";}toggleOrbitsBtn.addEventListener("click",()=>{showOrbits=!showOrbits;});canvas.addEventListener("click",showPlanetInfo);window.addEventListener("resize",handleResize);initStars();animate();//# sourceMappingURL=index.js.map",
                "language": "javascript"
            },
            {
                "filename": "index.html",
                "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><title>Solar System Orbit Simulator</title><style>body{background-color:#000;margin:0;font-family:Arial,sans-serif;overflow:hidden}#canvas{display:block}#controls{color:#fff;position:absolute;top:10px;left:10px}#info{color:#fff;background-color:#000000b3;border-radius:5px;padding:10px;display:none;position:absolute;top:10px;right:10px}.slider{width:200px}</style></head><body><canvas id="canvas"></canvas><div id="controls"><label for="speed">Orbit Speed:</label><input type="range" id="speed" class="slider" min="0.1" max="5" step="0.1" value="1" /><button id="toggleOrbits">Toggle Orbit Paths</button></div><div id="info"></div><script src="./index.js"></script></body></html>",
                "language": "html"
            }
        ],
        "installation_commands": "null",
        "additional_notes": "The code uses built-in libraries so no additional commands are required."
    }
    </example_answer_1>

    <example_question_2>:
      "Create a web page that displays an interactive piano visualization using HTML, CSS, and JavaScript. The piano should have 88 keys (52 white keys and 36 black keys). Implement the following user interactions:

      1. When the user hovers over a key, it should visually highlight to indicate it can be played.

      2. Clicking on a key should produce a pressing animation and play a corresponding piano note sound.

      3. Implement a slider that adjusts the piano's volume, affecting the loudness of the notes played when keys are clicked.

      Ensure the visualization is responsive and works well on different screen sizes. Use only built-in JavaScript libraries and features for this implementation.
      Note:
      - The visualization should be implemented in JavaScript with HTML and CSS.
      - Ensure that the output has both index.js and index.html files"
    </example_question_2>

    <example_answer_2>
    {
        "files": [
            {
                "filename": "index.js",
                "content": "const pianoKeys = [{note: 'A0', type: 'white'}, {note: 'A#0', type: 'black'}, {note: 'B0', type: 'white'}, {note: 'C1', type: 'white'}, {note: 'C#1', type: 'black'}, {note: 'D1', type: 'white'}, {note: 'D#1', type: 'black'}, {note: 'E1', type: 'white'}, {note: 'F1', type: 'white'}, {note: 'F#1', type: 'black'}, {note: 'G1', type: 'white'}, {note: 'G#1', type: 'black'}, {note: 'A1', type: 'white'}, {note: 'A#1', type: 'black'}, {note: 'B1', type: 'white'}, {note: 'C2', type: 'white'}, {note: 'C#2', type: 'black'}, {note: 'D2', type: 'white'}, {note: 'D#2', type: 'black'}, {note: 'E2', type: 'white'}, {note: 'F2', type: 'white'}, {note: 'F#2', type: 'black'}, {note: 'G2', type: 'white'}, {note: 'G#2', type: 'black'}, {note: 'A2', type: 'white'}, {note: 'A#2', type: 'black'}, {note: 'B2', type: 'white'}, {note: 'C3', type: 'white'}, {note: 'C#3', type: 'black'}, {note: 'D3', type: 'white'}, {note: 'D#3', type: 'black'}, {note: 'E3', type: 'white'}, {note: 'F3', type: 'white'}, {note: 'F#3', type: 'black'}, {note: 'G3', type: 'white'}, {note: 'G#3', type: 'black'}, {note: 'A3', type: 'white'}, {note: 'A#3', type: 'black'}, {note: 'B3', type: 'white'}, {note: 'C4', type: 'white'}, {note: 'C#4', type: 'black'}, {note: 'D4', type: 'white'}, {note: 'D#4', type: 'black'}, {note: 'E4', type: 'white'}, {note: 'F4', type: 'white'}, {note: 'F#4', type: 'black'}, {note: 'G4', type: 'white'}, {note: 'G#4', type: 'black'}, {note: 'A4', type: 'white'}, {note: 'A#4', type: 'black'}, {note: 'B4', type: 'white'}, {note: 'C5', type: 'white'}, {note: 'C#5', type: 'black'}, {note: 'D5', type: 'white'}, {note: 'D#5', type: 'black'}, {note: 'E5', type: 'white'}, {note: 'F5', type: 'white'}, {note: 'F#5', type: 'black'}, {note: 'G5', type: 'white'}, {note: 'G#5', type: 'black'}, {note: 'A5', type: 'white'}, {note: 'A#5', type: 'black'}, {note: 'B5', type: 'white'}, {note: 'C6', type: 'white'}, {note: 'C#6', type: 'black'}, {note: 'D6', type: 'white'}, {note: 'D#6', type: 'black'}, {note: 'E6', type: 'white'}, {note: 'F6', type: 'white'}, {note: 'F#6', type: 'black'}, {note: 'G6', type: 'white'}, {note: 'G#6', type: 'black'}, {note: 'A6', type: 'white'}, {note: 'A#6', type: 'black'}, {note: 'B6', type: 'white'}, {note: 'C7', type: 'white'}, {note: 'C#7', type: 'black'}, {note: 'D7', type: 'white'}, {note: 'D#7', type: 'black'}, {note: 'E7', type: 'white'}, {note: 'F7', type: 'white'}, {note: 'F#7', type: 'black'}, {note: 'G7', type: 'white'}, {note: 'G#7', type: 'black'}, {note: 'A7', type: 'white'}, {note: 'A#7', type: 'black'}, {note: 'B7', type: 'white'}, {note: 'C8', type: 'white'}]; const piano = document.getElementById('piano'); const volumeSlider = document.getElementById('volumeSlider'); let audioContext; function createKey(note, type) { const key = document.createElement('div'); key.className = `key ${type}-key`; key.dataset.note = note; key.addEventListener('mousedown', playNote); key.addEventListener('mouseup', stopNote); key.addEventListener('mouseleave', stopNote); return key; } function initializePiano() { pianoKeys.forEach(key => { piano.appendChild(createKey(key.note, key.type)); }); } function playNote(event) { if (!audioContext) { audioContext = new (window.AudioContext || window.webkitAudioContext)(); } const note = event.target.dataset.note; const frequency = getFrequency(note); const oscillator = audioContext.createOscillator(); const gainNode = audioContext.createGain(); oscillator.type = 'sine'; oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime); gainNode.gain.setValueAtTime(parseFloat(volumeSlider.value), audioContext.currentTime); gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 1); oscillator.connect(gainNode); gainNode.connect(audioContext.destination); oscillator.start(); oscillator.stop(audioContext.currentTime + 1); event.target.classList.add('active'); } function stopNote(event) { event.target.classList.remove('active'); } function getFrequency(note) { const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']; const octave = parseInt(note.slice(-1)); const semitone = notes.indexOf(note.slice(0, -1)); return 440 * Math.pow(2, (octave - 4) + (semitone - 9) / 12); } initializePiano();",
                "language": "javascript"
            },
            {
                "filename": "index.html",
                "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Interactive Piano Visualization</title><style>body{background:linear-gradient(#1a2a6c,#b21f1f,#fdbb2d);justify-content:center;align-items:center;min-height:100vh;margin:0;padding:0;font-family:Arial,sans-serif;display:flex}.piano-container{background-color:#222;border-radius:10px;padding:20px;box-shadow:0 0 20px #00000080}.piano{display:flex;position:relative}.key{cursor:pointer;transition:all .1s;position:relative}.white-key{z-index:1;background:linear-gradient(#f0f0f0,#fff);border:1px solid #ccc;border-radius:0 0 5px 5px;width:40px;height:200px}.black-key{z-index:2;background:linear-gradient(#333,#000);border-radius:0 0 3px 3px;width:25px;height:120px;margin-left:-12.5px;margin-right:-12.5px}.white-key:hover{background:linear-gradient(#e0e0e0,#f5f5f5)}.black-key:hover{background:linear-gradient(#444,#222)}.white-key:active,.white-key.active{background:linear-gradient(#d0d0d0,#e5e5e5);transform:translateY(2px)}.black-key:active,.black-key.active{background:linear-gradient(#555,#333);transform:translateY(2px)}.volume-control{color:#fff;justify-content:center;align-items:center;margin-top:20px;display:flex}.volume-slider{width:200px;margin:0 10px}</style></head><body><div class="piano-container"><div class="piano" id="piano"></div><div class="volume-control"><span>Volume:</span><input type="range" min="0" max="1" step="0.1" value="0.5" class="volume-slider" id="volumeSlider"></div></div><script src="/index.js"></script></body></html>",
                "language": "html"
            }
        ],
        "installation_commands": "null",
        "additional_notes": "The code uses built-in libraries so no additional commands are required."
    },
    </example_answer_2>

    <example_question_3>
    "Create a web page that visualizes a desert landscape using HTML, CSS, and JavaScript. The visualization should include sand dunes, a sun, and at least one cactus. Implement the following interactive features:

    1. When the user moves their mouse across the screen, small dust particles should appear and follow the mouse movement, simulating a light breeze in the desert.

    2. Allow the user to click anywhere on the screen to 'plant' a new cactus at that location. The cactus should grow from small to full size over a short period of time.

    Ensure that the visualization is responsive and works well on different screen sizes. Use only built-in JavaScript functions and avoid external libraries.
    Note:
    - The visualization should be implemented in JavaScript with HTML and CSS.
    - Ensure that the output has both index.js and index.html files"
    </example_question_3>

    <example_answer_3>
    {
    "files": [
        {
            "filename": "index.js",
            "content": "document.addEventListener("DOMContentLoaded",()=>{const desert=document.getElementById("desert");const dustParticles=[];createCactus(window.innerWidth/2,window.innerHeight*0.7);desert.addEventListener("mousemove",(e)=>{createDustParticle(e.clientX,e.clientY)});desert.addEventListener("click",(e)=>{createCactus(e.clientX,e.clientY)});function createCactus(x,y){const cactus=document.createElement("div");cactus.className="cactus";cactus.style.left=`${x}px`;cactus.style.bottom=`${window.innerHeight-y}px`;cactus.style.height="0px";desert.appendChild(cactus);setTimeout(()=>{cactus.style.height="100px"},50)}function createDustParticle(x,y){const dust=document.createElement("div");dust.className="dust";dust.style.left=`${x}px`;dust.style.top=`${y}px`;desert.appendChild(dust);dustParticles.push(dust);if(dustParticles.length>50){const oldDust=dustParticles.shift();oldDust.remove()}animateDust(dust)}function animateDust(dust){let opacity=1;let size=3;let posX=parseFloat(dust.style.left);let posY=parseFloat(dust.style.top);function updateDust(){opacity-=0.02;size-=0.05;posX+=(Math.random()-0.5)*2;posY-=0.5;if(opacity<=0||size<=0){dust.remove();return}dust.style.opacity=opacity;dust.style.width=`${size}px`;dust.style.height=`${size}px`;dust.style.left=`${posX}px`;dust.style.top=`${posY}px`;requestAnimationFrame(updateDust)}requestAnimationFrame(updateDust)}window.addEventListener("resize",()=>{const cacti=document.querySelectorAll(".cactus");cacti.forEach((cactus)=>{const bottomPercentage=parseFloat(cactus.style.bottom)/window.innerHeight*100;cactus.style.bottom=`${bottomPercentage}%`})})});",
            "language": "javascript"
        },
        {
            "filename": "index.html",
            "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Desert Landscape</title><style>body, html {height: 100%;margin: 0;padding: 0;overflow: hidden;}#desert {background: linear-gradient(gold, orange);width: 100%;height: 100%;position: relative;overflow: hidden;}.sand-dune {background: tan;border-radius: 50% 50% 0 0;width: 100%;height: 30%;position: absolute;bottom: 0;}#sun {background: tomato;border-radius: 50%;width: 100px;height: 100px;position: absolute;top: 10%;left: 10%;box-shadow: 0 0 50px tomato;}.cactus {background: #2e8b57;border-radius: 10px;width: 40px;transition: height 1s ease-out;position: absolute;bottom: 30%;}.cactus:before, .cactus:after {content: "";background: #2e8b57;border-radius: 10px;width: 20px;height: 30px;position: absolute;}.cactus:before {top: 30%;left: -15px;transform: rotate(45deg);}.cactus:after {top: 60%;right: -15px;transform: rotate(-45deg);}.dust {pointer-events: none;background: #d2b48cb3;border-radius: 50%;width: 3px;height: 3px;position: absolute;}</style></head><body><div id="desert"><div id="sun"></div><div class="sand-dune"></div></div><script src="/index.js"></script></body></html>",
            "language": "html"
        }
    ],
    "installation_commands": "null",
    "additional_notes": "The code uses built-in libraries so no additional commands are required."
    },
    </example_answer_3>
    """
    return EXAMPLE_OUTPUTS


def get_games_examples() -> str:
    indexjs_2048 = "const gameBoard=document.getElementById('game-board');const scoreElement=document.getElementById('score');const bestScoreElement=document.getElementById('best-score');const undoButton=document.getElementById('undo-btn');const newGameButton=document.getElementById('new-game-btn');const colorSelect=document.getElementById('color-select');let board=[];let score=0;let bestScore=0;let gameHistory=[];const colorSchemes={default:{2:'#eee4da',4:'#ede0c8',8:'#f2b179',16:'#f59563',32:'#f67c5f',64:'#f65e3b',128:'#edcf72',256:'#edcc61',512:'#edc850',1024:'#edc53f',2048:'#edc22e'},dark:{2:'#635B5B',4:'#7A6F6F',8:'#8F8383',16:'#A49797',32:'#B9ABAB',64:'#CEBFBF',128:'#E3D3D3',256:'#F8E7E7',512:'#FFFDFD',1024:'#FFFFFF',2048:'#FFF700'},pastel:{2:'#FFD1DC',4:'#FFB3BA',8:'#FFDFBA',16:'#FFFFBA',32:'#BAFFC9',64:'#BAE1FF',128:'#D0BAFF',256:'#F4BAFF',512:'#FFB3BA',1024:'#FFDFBA',2048:'#FFFFBA'}};function initializeGame(){board=Array(4).fill().map(()=>Array(4).fill(0));score=0;gameHistory=[];addNewTile();addNewTile();updateBoard();}function addNewTile(){const emptyTiles=[];for(let i=0;i<4;i++){for(let j=0;j<4;j++){if(board[i][j]===0){emptyTiles.push({row:i,col:j});}}}if(emptyTiles.length>0){const{row,col}=emptyTiles[Math.floor(Math.random()*emptyTiles.length)];board[row][col]=Math.random()<0.9?2:4;}}function updateBoard(){gameBoard.innerHTML='';for(let i=0;i<4;i++){for(let j=0;j<4;j++){const tile=document.createElement('div');tile.className='tile';tile.textContent=board[i][j]||'';if(board[i][j]!==0){const colorScheme=colorSchemes[colorSelect.value];tile.style.backgroundColor=colorScheme[board[i][j]]||'#3c3a32';tile.style.color=board[i][j]<=4?'#776e65':'#f9f6f2';}gameBoard.appendChild(tile);}}scoreElement.textContent=`Score: ${score}`;if(score>bestScore){bestScore=score;bestScoreElement.textContent=`Best: ${bestScore}`;}}function move(direction){gameHistory.push({board:JSON.parse(JSON.stringify(board)),score});let moved=false;const rotatedBoard=rotateBoard(direction);for(let i=0;i<4;i++){const row=rotatedBoard[i].filter(tile=>tile!==0);for(let j=0;j<row.length-1;j++){if(row[j]===row[j+1]){row[j]*=2;score+=row[j];row[j+1]=0;moved=true;}}const newRow=row.filter(tile=>tile!==0);while(newRow.length<4){newRow.push(0);}if(JSON.stringify(rotatedBoard[i])!==JSON.stringify(newRow)){moved=true;}rotatedBoard[i]=newRow;}board=rotateBoard(direction,true,rotatedBoard);if(moved){addNewTile();updateBoard();if(isGameOver()){alert('Game Over!');}else if(hasWon()){alert('Congratulations! You've reached 2048!');}}}function rotateBoard(direction,reverse=false,inputBoard=board){let rotatedBoard=JSON.parse(JSON.stringify(inputBoard));const transpose=()=>{for(let i=0;i<4;i++){for(let j=i;j<4;j++){[rotatedBoard[i][j],rotatedBoard[j][i]]=[rotatedBoard[j][i],rotatedBoard[i][j]];}}}; const reverse_rows=()=>{for(let i=0;i<4;i++){rotatedBoard[i].reverse();}};if(!reverse){if(direction==='up')transpose();if(direction==='right')reverse_rows();if(direction==='down'){transpose();reverse_rows();}}else{if(direction==='up')transpose();if(direction==='right')reverse_rows();if(direction==='down'){reverse_rows();transpose();}}return rotatedBoard;}function isGameOver(){for(let i=0;i<4;i++){for(let j=0;j<4;j++){if(board[i][j]===0)return false;if(i<3&&board[i][j]===board[i+1][j])return false;if(j<3&&board[i][j]===board[i][j+1])return false;}}return true;}function hasWon(){for(let i=0;i<4;i++){for(let j=0;j<4;j++){if(board[i][j]===2048)return true;}}return false;}function undo(){if(gameHistory.length>0){const lastState=gameHistory.pop();board=lastState.board;score=lastState.score;updateBoard();}}document.addEventListener('keydown',(e)=>{e.preventDefault();switch(e.key){case'ArrowUp':move('up');break;case'ArrowDown':move('down');break;case'ArrowLeft':move('left');break;case'ArrowRight':move('right');break;}});let touchStartX,touchStartY;gameBoard.addEventListener('touchstart',(e)=>{touchStartX=e.touches[0].clientX;touchStartY=e.touches[0].clientY;});gameBoard.addEventListener('touchend',(e)=>{if(!touchStartX||!touchStartY)return;const touchEndX=e.changedTouches[0].clientX;const touchEndY=e.changedTouches[0].clientY;const deltaX=touchEndX-touchStartX;const deltaY=touchEndY-touchStartY;if(Math.abs(deltaX)>Math.abs(deltaY)){if(deltaX>0){move('right');}else{move('left');}}else{if(deltaY>0){move('down');}else{move('up');}}touchStartX=null;touchStartY=null;});undoButton.addEventListener('click',undo);newGameButton.addEventListener('click',initializeGame);colorSelect.addEventListener('change',updateBoard);initializeGame();"
    indexhtml_2048 = """<!DOCTYPE html><html lang="en"><head><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com; style-src 'unsafe-inline'; img-src data: blob: https://threejsfundamentals.org; connect-src 'none'; form-action 'none'; base-uri 'none';"><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>2048 Game</title><style>body{font-family:Arial,sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;background-color:#faf8ef}#game-container{text-align:center}#game-board{display:grid;grid-template-columns:repeat(4,1fr);grid-gap:15px;background-color:#bbada0;border-radius:5px;padding:15px;margin-bottom:20px}.tile{width:100px;height:100px;background-color:#cdc1b4;border-radius:3px;display:flex;justify-content:center;align-items:center;font-size:36px;font-weight:bold;color:#776e65;transition:all .1s ease-in-out}#score,#best-score{display:inline-block;padding:10px 20px;background-color:#bbada0;border-radius:3px;color:white;font-size:18px;margin:0 10px}#undo-btn,#new-game-btn{padding:10px 20px;font-size:18px;background-color:#8f7a66;color:white;border:none;border-radius:3px;cursor:pointer;margin:10px}#color-scheme{margin-top:20px}</style></head><body><div id="game-container"><div id="game-board"></div><div><span id="score">Score: 0</span><span id="best-score">Best: 0</span></div><button id="undo-btn">Undo</button><button id="new-game-btn">New Game</button><div id="color-scheme"><label for="color-select">Color Scheme:</label><select id="color-select"><option value="default">Default</option><option value="dark">Dark</option><option value="pastel">Pastel</option></select></div></div><script src="index.js"></script></body></html>"""

    EXAMPLE_OUTPUTS = """
        <example_question_1>:
        Create a fully functional 2048 game with the following features:

        -4x4 grid layout
        -Smooth tile sliding and merging animations
        -Score tracking and display
        -Game over detection when no more moves are possible
        -Win condition when 2048 tile is created
        -Standard keyboard controls (arrow keys)
        -Touch/swipe support for mobile devices
        -Use only HTML, JavaScript, and CSS without any external dependencies, libraries, or frameworks.
        -Generate all graphics within the code, avoiding reliance on external image files.
        -Ensure the game runs in an HTML iframe without requiring any additional setup.
        -Provide complete, runnable code without placeholders or omissions.
        -Proactively address common bugs and pitfalls in 2048 game implementations.
        -As the game will run in a self-contained HTML iframe, ensure that the code does not use any local or session storage.
        -Ensure that any keystrokes used do not trigger the default browser behaviour. If the user uses arrow keys to play, it should not also trigger scrolling of the browser.

        Include additional cool features that enhance the game experience, such as:
        -Undo functionality
        -Best score tracking
        -Color scheme customization option
        -Responsive design for various screen sizes

        Prioritize code completeness, robustness, and readiness for immediate execution.
        Structure the response as follows:
        a. Brief introduction explaining the game and its features
        b. HTML code (including inline CSS if applicable)
        c. JavaScript code
        d. Any additional CSS in a separate <style> tag or file
        e. Instructions for running the game

        Remember to focus on delivering a complete, functional, and engaging 2048 game implementation using web technologies that can be easily copied and pasted into an HTML file to run immediately in a web browser.
        Note:
        - Your output should be implemented in JavaScript with HTML and CSS.
        - Ensure that the output has both index.js and index.html files
        </example_question_1>:
        
        <example_answer_1>
        {{
            "files": [
                {{
                    "filename": "index.js",
                    "content": "{indexjs_2048}",
                    "language": "javascript",
                }},
                {{
                    "filename": "index.html",
                    "content": "{indexhtml_2048}",
                    "language": "html",
                }}
            ],
            "installation_commands": "null",
            "additional_notes": "The code uses built-in libraries so no additional commands are required."
        }}
        </example_answer_1>
    """
    return EXAMPLE_OUTPUTS
