import random

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


def _get_game_answer_examples() -> str:
    example_1 = """
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
    """
    example_2 = """
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
    example_3 = """
        <example_input_3>
            Implement a fun web game called 'Perfect Park' where players must skillfully maneuver a delivery van into increasingly challenging parking spots while racing against time.

            Features:
            - Create a 2D game area representing a street view with multiple parking spots.
            - Display a delivery van sprite that can be controlled by the player.
            - Implement smooth van movement using arrow keys, with realistic turning mechanics. Ensure default key behaviors are disabled.
            - Create visual parking spot boundaries using dashed lines.
            - Add randomly placed obstacles (other parked cars, trash bins, construction cones) that the van must avoid.
            - Display a timer counting down from 60 seconds.
            - Implement a scoring system: +100 points for perfect parking (van completely within spot lines), +50 for acceptable parking (majority of van within lines).
            - Show a parking guide overlay when the van is near a valid parking spot, indicating if the current position would result in perfect or acceptable parking.
            - Add visual feedback when the van collides with obstacles (flashing red).
            - Create a 'delivery complete' animation when successfully parked (brief celebration effect).
            - Display current score and high score at the top of the screen.
            - Show 'Game Over' screen when timer reaches zero, displaying final score and 'Play Again' button.
            - Generate new obstacle layouts each time the player successfully parks or starts a new game.

            User Actions:
            1. Use arrow keys to control the delivery van (Up/Down for forward/reverse, Left/Right for steering).
            2. Press Spacebar to 'lock in' your parking attempt when you think you're properly parked. If successful, gain points and move to next layout. If unsuccessful, lose 5 seconds from the timer.
        </example_input_3>
        <example_output_3>
            {
                "files": [
                    {
                        "filename": "index.js",
                        "content": "const canvas=document.getElementById('gameCanvas');const ctx=canvas.getContext('2d');const scoreElement=document.getElementById('score');const highScoreElement=document.getElementById('highScore');const timerElement=document.getElementById('timer');const gameOverScreen=document.getElementById('gameOver');const finalScoreElement=document.getElementById('finalScore');const playAgainButton=document.getElementById('playAgain');let canvasWidth=800;let canvasHeight=800;let scale=1;function resizeCanvas(){const container=document.getElementById('gameContainer');const containerWidth=container.clientWidth;const containerHeight=container.clientHeight;scale=Math.min(containerWidth/canvasWidth,containerHeight/canvasHeight);canvas.width=canvasWidth*scale;canvas.height=canvasHeight*scale;ctx.scale(scale,scale);}window.addEventListener('resize',resizeCanvas);resizeCanvas();const VAN_WIDTH=60;const VAN_HEIGHT=30;const van={x:canvasWidth/2,y:canvasHeight-100,angle:0,speed:0,turning:0,};const OBSTACLE_TYPES=[{width:50,height:30,color:'#4A4A4A'},{width:20,height:20,color:'#FF6B6B'},{width:15,height:40,color:'#FFA500'}];let obstacles=[];let parkingSpot={x:0,y:0,width:80,height:40};let score=0;let highScore=0;let timeLeft=60;let isParked=false;let gameOver=false;let colliding=false;let celebrating=false;let celebrationTimer=0;function createObstacles(){obstacles=[];const numObstacles=Math.floor(Math.random()*5)+5;for(let i=0;i<numObstacles;i++){const type=OBSTACLE_TYPES[Math.floor(Math.random()*OBSTACLE_TYPES.length)];const obstacle={x:Math.random()*(canvasWidth-type.width),y:Math.random()*(canvasHeight-type.height),width:type.width,height:type.height,color:type.color,};if(!checkCollision(obstacle,parkingSpot)){obstacles.push(obstacle);}}}function createParkingSpot(){parkingSpot={x:Math.random()*(canvasWidth-100)+50,y:Math.random()*(canvasHeight-200)+50,width:80,height:40,};}function drawVan(){ctx.save();ctx.translate(van.x,van.y);ctx.rotate(van.angle);ctx.fillStyle='#2E86DE';ctx.fillRect(-VAN_WIDTH/2,-VAN_HEIGHT/2,VAN_WIDTH,VAN_HEIGHT);ctx.fillStyle='#87CEEB';ctx.fillRect(VAN_WIDTH/4,-VAN_HEIGHT/2,VAN_WIDTH/4,VAN_HEIGHT/3);if(colliding){ctx.strokeStyle='#FF0000';ctx.lineWidth=3;ctx.strokeRect(-VAN_WIDTH/2,-VAN_HEIGHT/2,VAN_WIDTH,VAN_HEIGHT);}ctx.restore();}function drawParkingSpot(){ctx.setLineDash([5,5]);ctx.strokeStyle='#FFFFFF';ctx.lineWidth=2;ctx.strokeRect(parkingSpot.x,parkingSpot.y,parkingSpot.width,parkingSpot.height);ctx.setLineDash([]);}function drawObstacles(){obstacles.forEach(obstacle=>{ctx.fillStyle=obstacle.color;ctx.fillRect(obstacle.x,obstacle.y,obstacle.width,obstacle.height);});}function drawParkedEffect(){if(celebrating){ctx.fillStyle=`rgba(255, 215, 0, ${Math.sin(celebrationTimer*0.1)*0.5+0.5})`;ctx.fillRect(parkingSpot.x,parkingSpot.y,parkingSpot.width,parkingSpot.height);}}function checkCollision(rect1,rect2){return rect1.x<rect2.x+rect2.width&&rect1.x+rect1.width>rect2.x&&rect1.y<rect2.y+rect2.height&&rect1.y+rect1.height>rect2.y;}function checkVanCollisions(){const vanBounds={x:van.x-VAN_WIDTH/2,y:van.y-VAN_HEIGHT/2,width:VAN_WIDTH,height:VAN_HEIGHT,};colliding=false;for(const obstacle of obstacles){if(checkCollision(vanBounds,obstacle)){colliding=true;break;}}}function checkParking(){const vanBounds={x:van.x-VAN_WIDTH/2,y:van.y-VAN_HEIGHT/2,width:VAN_WIDTH,height:VAN_HEIGHT,};if(checkCollision(vanBounds,parkingSpot)){const overlapX=Math.min(vanBounds.x+vanBounds.width,parkingSpot.x+parkingSpot.width)-Math.max(vanBounds.x,parkingSpot.x);const overlapY=Math.min(vanBounds.y+vanBounds.height,parkingSpot.y+parkingSpot.height)-Math.max(vanBounds.y,parkingSpot.y);const overlapArea=(overlapX*overlapY)/(VAN_WIDTH*VAN_HEIGHT);if(overlapArea>0.9&&Math.abs(van.angle%(Math.PI*2))<0.1){return'perfect';}else if(overlapArea>0.6){return'acceptable';}}return'none';}function updateVan(){if(!isParked){van.x+=Math.cos(van.angle)*van.speed;van.y+=Math.sin(van.angle)*van.speed;van.angle+=van.turning*0.05;van.speed*=0.95;van.turning*=0.95;van.x=Math.max(VAN_WIDTH/2,Math.min(canvasWidth-VAN_WIDTH/2,van.x));van.y=Math.max(VAN_HEIGHT/2,Math.min(canvasHeight-VAN_HEIGHT/2,van.y));}}function drawParkingGuide(){const parkingStatus=checkParking();if(parkingStatus!=='none'){ctx.fillStyle=parkingStatus==='perfect'?'rgba(0, 255, 0, 0.3)':'rgba(255, 255, 0, 0.3)';ctx.fillRect(parkingSpot.x,parkingSpot.y,parkingSpot.width,parkingSpot.height);}}function updateGame(){if(!gameOver){updateVan();checkVanCollisions();if(celebrating){celebrationTimer++;if(celebrationTimer>60){celebrating=false;celebrationTimer=0;nextLevel();}}}}function drawGame(){ctx.fillStyle='#333333';ctx.fillRect(0,0,canvasWidth,canvasHeight);drawParkingSpot();drawObstacles();drawVan();drawParkingGuide();drawParkedEffect();}function nextLevel(){isParked=false;van.x=canvasWidth/2;van.y=canvasHeight-100;van.angle=0;van.speed=0;van.turning=0;createParkingSpot();createObstacles();}function startGame(){score=0;timeLeft=60;gameOver=false;isParked=false;celebrating=false;highScore=Math.max(highScore,score);nextLevel();gameOverScreen.style.display='none';gameLoop();timerLoop();}function endGame(){gameOver=true;highScore=Math.max(highScore,score);finalScoreElement.textContent=score;gameOverScreen.style.display='flex';}function attemptParking(){if(!isParked&&!celebrating){const parkingStatus=checkParking();if(parkingStatus==='perfect'){score+=100;isParked=true;celebrating=true;}else if(parkingStatus==='acceptable'){score+=50;isParked=true;celebrating=true;}else{timeLeft=Math.max(0,timeLeft-5);}}}let lastTime=0;function gameLoop(currentTime){if(lastTime===0)lastTime=currentTime;const deltaTime=(currentTime-lastTime)/1000;lastTime=currentTime;if(!gameOver){updateGame();drawGame();scoreElement.textContent=`Score: ${score}`;highScoreElement.textContent=`High Score: ${highScore}`;requestAnimationFrame(gameLoop);}}function timerLoop(){if(!gameOver){timeLeft--;timerElement.textContent=`Time: ${timeLeft}s`;if(timeLeft<=0){endGame();}else{setTimeout(timerLoop,1000);}}}const keys={};window.addEventListener('keydown',e=>{if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Space'].includes(e.code)){e.preventDefault();keys[e.code]=true;}if(e.code==='Space'){attemptParking();}});window.addEventListener('keyup',e=>{if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Space'].includes(e.code)){e.preventDefault();keys[e.code]=false;}});setInterval(()=>{if(!isParked&&!gameOver){if(keys.ArrowUp)van.speed+=0.5;if(keys.ArrowDown)van.speed-=0.5;if(keys.ArrowLeft)van.turning-=0.1;if(keys.ArrowRight)van.turning+=0.1;}},1000/60);playAgainButton.addEventListener('click',startGame);startGame();",
                        "language": "javascript"
                    },
                    {
                        "filename": "index.html",
                        "content": "<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1.0'><title>Perfect Park</title><style>body,html{margin:0;padding:0;height:100%;overflow:hidden;font-family:Arial,sans-serif}#gameContainer{position:relative;width:100vmin;height:100vmin;margin:auto;background:#333}#gameCanvas{position:absolute;top:0;left:0;width:100%;height:100%}#hud{position:absolute;top:10px;left:10px;right:10px;display:flex;justify-content:space-between;color:white;font-size:18px;text-shadow:2px 2px 4px rgba(0,0,0,0.5)}#gameOver{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,0.8);color:white;padding:20px;border-radius:10px;text-align:center;display:none;flex-direction:column;align-items:center}#playAgain{margin-top:20px;padding:10px 20px;font-size:18px;background:#4CAF50;color:white;border:none;border-radius:5px;cursor:pointer}#playAgain:hover{background:#45a049}</style></head><body><div id='gameContainer'><canvas id='gameCanvas'></canvas><div id='hud'><span id='score'>Score: 0</span><span id='timer'>Time: 60s</span><span id='highScore'>High Score: 0</span></div><div id='gameOver'><h2>Game Over!</h2><p>Final Score: <span id='finalScore'>0</span></p><button id='playAgain'>Play Again</button></div></div><script src='index.js'></script></body></html>",
                        "language": "html"
                    }
                ]
            }
        </example_output_3>
    """
    example_4 = """
        <example_input_4>
            Implement a fun, streamlined web game called 'Cyberspace Conquest' where the player navigates through cyberspace and defends against enemy malware.

            Features:
            - Create a 2D game area with a neon grid that scrolls horizontally in the background to represent cyberspace.
            - The game area must wrap around all edges (malware and players that go off one side appear on the opposite side).
            - The player controls a triangular hacker sprite to navigate through cyberspace. Player movement should resemble a spaceship.
            - The player must fire projectiles (maximum of 5 at one time) at enemy malware. The projectiles should travel a finite distance before disappearing.
            - Create enemy malware as irregular polygons that drift through cyberspace. The malware should move in straight lines at different angles and speeds.
            - When malware is hit by the player's projectiles, it should split into smaller malware, and the player's score should increase.
            - The player has 3 lives. If the player collides with malware, the player should lose a life, and become briefly invulnerable, before respawning at the center of the screen.
            - Show a game over screen when the player loses all their lives, showing the final score and a 'Play Again' button.
            - The game should display the player's score, high score and lives on the screen.
            - Use a cyberpunk colour scheme and aesthetic (deep purple as the background, neon pink for the HUD).

            User Actions:
            1. Use the arrow keys to navigate through cyberspace.
            2. Press the spacebar to fire projectiles at enemy malware.
        </example_input_4>
        <example_output_4>
            {
                "files": [
                    {
                        "filename": "index.js",
                        "content": "const canvas=document.getElementById("gameCanvas"),ctx=canvas.getContext("2d"),scoreElement=document.getElementById("score"),highScoreElement=document.getElementById("highScore"),livesElement=document.getElementById("lives"),gameOverScreen=document.getElementById("gameOver"),finalScoreElement=document.getElementById("finalScore"),playAgainButton=document.getElementById("playAgain"),GRID_SIZE=40,PLAYER_SIZE=20,PROJECTILE_SPEED=10,MALWARE_COUNT=4,player={x:400,y:400,angle:0,speed:0,turnSpeed:0,projectiles:[]},malwares=[],keys={};let canvasWidth=800,canvasHeight=800,scale=1,gridOffset=0,score=0,highScore=0,lives=3,gameOver=false,invulnerable=false,invulnerableTimer=0,lastTime=0;function resizeCanvas(){const e=document.getElementById("gameContainer");scale=Math.min(e.clientWidth/canvasWidth,e.clientHeight/canvasHeight),canvas.width=canvasWidth*scale,canvas.height=canvasHeight*scale,ctx.scale(scale,scale)}window.addEventListener("resize",resizeCanvas),resizeCanvas();class Projectile{constructor(e,t,i){this.x=e,this.y=t,this.angle=i,this.distance=0}move(){this.x+=Math.cos(this.angle)*PROJECTILE_SPEED,this.y+=Math.sin(this.angle)*PROJECTILE_SPEED,this.x=(this.x+canvasWidth)%canvasWidth,this.y=(this.y+canvasHeight)%canvasHeight,this.distance+=PROJECTILE_SPEED}draw(){ctx.strokeStyle="#00ff00",ctx.beginPath(),ctx.moveTo(this.x-Math.cos(this.angle)*5,this.y-Math.sin(this.angle)*5),ctx.lineTo(this.x+Math.cos(this.angle)*5,this.y+Math.sin(this.angle)*5),ctx.stroke()}}class Malware{constructor(e,t,i,s,a,n){this.x=e,this.y=t,this.size=i,this.angle=s,this.speed=a,this.points=n||this.generatePoints()}generatePoints(){const e=[];for(let t=0;t<Math.floor(3*Math.random())+5;t++){const i=t/(Math.floor(3*Math.random())+5)*Math.PI*2,s=this.size*(.8+.4*Math.random());e.push({x:Math.cos(i)*s,y:Math.sin(i)*s})}return e}move(){this.x+=Math.cos(this.angle)*this.speed,this.y+=Math.sin(this.angle)*this.speed,this.x=(this.x+canvasWidth)%canvasWidth,this.y=(this.y+canvasHeight)%canvasHeight}draw(){ctx.strokeStyle="#ff1493",ctx.beginPath(),ctx.moveTo(this.x+this.points[0].x,this.y+this.points[0].y);for(let e=1;e<this.points.length;e++)ctx.lineTo(this.x+this.points[e].x,this.y+this.points[e].y);ctx.closePath(),ctx.stroke(),ctx.strokeStyle="#ff69b4",ctx.beginPath();for(let e=0;e<this.points.length;e++){const t=this.points[e],i=this.points[(e+2)%this.points.length];ctx.moveTo(this.x+t.x,this.y+t.y),ctx.lineTo(this.x+i.x,this.y+i.y)}ctx.stroke()}}function createMalware(e,t,i){return new Malware(e||Math.random()*canvasWidth,t||Math.random()*canvasHeight,i||20*Math.random()+30,Math.random()*Math.PI*2,1.5*Math.random()+.5)}function drawGrid(){ctx.strokeStyle="#2E1A47",gridOffset=(gridOffset+1)%GRID_SIZE;for(let e=-GRID_SIZE;e<=canvasWidth+GRID_SIZE;e+=GRID_SIZE)ctx.beginPath(),ctx.moveTo(e+gridOffset,0),ctx.lineTo(e+gridOffset,canvasHeight),ctx.stroke();for(let e=0;e<=canvasHeight;e+=GRID_SIZE)ctx.beginPath(),ctx.moveTo(0,e),ctx.lineTo(canvasWidth,e),ctx.stroke()}function drawPlayer(){ctx.save(),ctx.translate(player.x,player.y),ctx.rotate(player.angle),ctx.strokeStyle=invulnerable?"#ffffff":"#00ffff",ctx.beginPath(),ctx.moveTo(PLAYER_SIZE,0),ctx.lineTo(-PLAYER_SIZE/2,-PLAYER_SIZE/2),ctx.lineTo(-PLAYER_SIZE/2,PLAYER_SIZE/2),ctx.closePath(),ctx.stroke(),invulnerable||(ctx.strokeStyle="#00cccc",ctx.beginPath(),ctx.moveTo(PLAYER_SIZE/2,0),ctx.lineTo(-PLAYER_SIZE/4,-PLAYER_SIZE/4),ctx.lineTo(-PLAYER_SIZE/4,PLAYER_SIZE/4),ctx.closePath(),ctx.stroke()),ctx.restore()}function updatePlayer(){player.angle+=player.turnSpeed,player.x+=Math.cos(player.angle)*player.speed,player.y+=Math.sin(player.angle)*player.speed,player.x=(player.x+canvasWidth)%canvasWidth,player.y=(player.y+canvasHeight)%canvasHeight,player.speed*=.995,player.turnSpeed*=.92,invulnerable&&(invulnerableTimer--,invulnerableTimer<=0&&(invulnerable=!1))}function fireProjectile(){player.projectiles.length<5&&player.projectiles.push(new Projectile(player.x+Math.cos(player.angle)*PLAYER_SIZE,player.y+Math.sin(player.angle)*PLAYER_SIZE,player.angle))}function updateProjectiles(){for(let e=player.projectiles.length-1;e>=0;e--){const t=player.projectiles[e];t.move(),t.distance>300&&player.projectiles.splice(e,1)}}function checkCollisions(){if(!invulnerable)for(let e=0;e<malwares.length;e++){const t=malwares[e],i=player.x-t.x,s=player.y-t.y;if(Math.sqrt(i*i+s*s)<t.size+PLAYER_SIZE/2){lives--,invulnerable=!0,invulnerableTimer=120,player.x=canvasWidth/2,player.y=canvasHeight/2,player.speed=0,lives<=0&&endGame();break}}for(let e=player.projectiles.length-1;e>=0;e--){const t=player.projectiles[e];for(let i=malwares.length-1;i>=0;i--){const s=malwares[i],a=t.x-s.x,n=t.y-s.y;if(Math.sqrt(a*a+n*n)<s.size){player.projectiles.splice(e,1),s.size>20&&(malwares.push(createMalware(s.x,s.y,.6*s.size)),malwares.push(createMalware(s.x,s.y,.6*s.size))),malwares.splice(i,1),score+=Math.floor(s.size),malwares.length<MALWARE_COUNT&&malwares.push(createMalware());break}}}}function updateGame(){gameOver||(updatePlayer(),updateProjectiles(),malwares.forEach(e=>e.move()),checkCollisions())}function drawGame(){ctx.fillStyle="#1a0033",ctx.fillRect(0,0,canvasWidth,canvasHeight),drawGrid(),malwares.forEach(e=>e.draw()),player.projectiles.forEach(e=>e.draw()),drawPlayer()}function updateHUD(){scoreElement.textContent=`Score: ${score}`,highScoreElement.textContent=`High Score: ${highScore}`,livesElement.textContent=`Lives: ${lives}`}function startGame(){score=0,lives=3,gameOver=!1,invulnerable=!1,player.x=canvasWidth/2,player.y=canvasHeight/2,player.angle=0,player.speed=0,player.turnSpeed=0,player.projectiles=[],malwares.length=0;for(let e=0;e<MALWARE_COUNT;e++)malwares.push(createMalware());gameOverScreen.style.display="none",gameLoop()}function endGame(){gameOver=!0,highScore=Math.max(highScore,score),finalScoreElement.textContent=score,gameOverScreen.style.display="flex"}function gameLoop(e){0===lastTime&&(lastTime=e);const t=(e-lastTime)/1e3;lastTime=e,gameOver||(updateGame(),drawGame(),updateHUD(),requestAnimationFrame(gameLoop))}window.addEventListener("keydown",e=>{["ArrowUp","ArrowDown","ArrowLeft","ArrowRight","Space"].includes(e.code)&&(e.preventDefault(),keys[e.code]=!0),"Space"===e.code&&fireProjectile()}),window.addEventListener("keyup",e=>{["ArrowUp","ArrowDown","ArrowLeft","ArrowRight","Space"].includes(e.code)&&(e.preventDefault(),keys[e.code]=!1)}),setInterval(()=>{gameOver||(keys.ArrowUp&&(player.speed+=.15),keys.ArrowDown&&(player.speed-=.08),keys.ArrowLeft&&(player.turnSpeed-=.02),keys.ArrowRight&&(player.turnSpeed+=.02))},1e3/60),playAgainButton.addEventListener("click",startGame),startGame();",
                        "language": "javascript"
                    },
                    {
                        "filename": "index.html",
                        "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width,initial-scale=1.0" /><title>Cyberspace Conquest</title><style>body,html{margin:0;padding:0;height:100%;overflow:hidden;font-family:"Courier New",monospace;background:#000}#gameContainer{position:relative;width:100vmin;height:100vmin;margin:auto}#gameCanvas{position:absolute;top:0;left:0;width:100%;height:100%}#hud{position:absolute;top:10px;left:10px;right:10px;display:flex;justify-content:space-between;color:#ff1493;font-size:18px;text-shadow:0 0 10px #ff1493}#gameOver{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(26,0,51,0.9);color:#00ffff;padding:20px;border-radius:10px;text-align:center;display:none;flex-direction:column;align-items:center;border:2px solid #ff1493;box-shadow:0 0 20px #ff1493}#playAgain{margin-top:20px;padding:10px 20px;font-size:18px;background:#1a0033;color:#00ffff;border:2px solid #00ffff;border-radius:5px;cursor:pointer;text-transform:uppercase;letter-spacing:2px}#playAgain:hover{background:#2a0053;box-shadow:0 0 10px #00ffff}</style></head><body><div id="gameContainer"><canvas id="gameCanvas"></canvas><div id="hud"><span id="score">Score: 0</span><span id="highScore">High Score: 0</span><span id="lives">Lives: 3</span></div><div id="gameOver"><h2>SYSTEM COMPROMISED</h2><p>Final Score: <span id="finalScore">0</span></p><button id="playAgain">Play Again</button></div></div><script src="index.js"></script></body></html>",
                        "language": "html"
                    }
                ]
            }
        </example_output_4>
    """
    example_5 = """
        <example_input_5>
            Implement a fun web game called "Beat Match Master" where players must catch falling music notes by clicking at the right moment while avoiding disruptive elements.

            Features:
            - Create a vertical game area with a neon grid background that pulses to a constant rhythm (60 BPM).
            - Display three vertical "track lines" where notes can fall, colored in distinct neon colors (pink, cyan, green).
            - Generate music notes that fall down these track lines at a constant speed. The notes should be simple geometric shapes (circles, squares, triangles).
            - Each note should have a "perfect catch zone" at the bottom of its track line, visualized as a thin horizontal line.
            - Create visual feedback when notes are caught: successful catches create expanding rings of light, while misses create a brief static effect.
            - Add "disruption waves" that periodically move horizontally across the screen. These waves should be visually distinct (zigzag patterns) and move at varying speeds.
            - Display a score multiplier that increases with consecutive successful catches and resets on misses.
            - Show the current score prominently at the top of the screen with a retro digital display aesthetic.
            - Create a combo counter that tracks successive successful catches.
            - Add visual effects that intensify as the combo counter increases (background pulse becomes stronger, colors become more vibrant).
            - When the player reaches certain score thresholds, increase the speed and frequency of falling notes.
            - Display a "Game Over" screen when three consecutive notes are missed, showing final score and a "Play Again" button.
            - The game's color scheme should use bright neon colors against a dark background to create a club atmosphere.

            User Actions:
            1. Press the A, S, or D keys to catch notes in the left, middle, or right tracks respectively when they align with the catch zone.
            2. Press the spacebar to activate "Bass Drop" which slows down all notes and waves for 5 seconds (can be used once every 30 seconds).
        </example_input_5>
        <example_output_5>
            {
                "files": [
                    {
                        "filename": "index.js",
                        "content": "const canvas=document.getElementById("gameCanvas"),ctx=canvas.getContext("2d"),scoreElement=document.getElementById("score"),comboElement=document.getElementById("combo"),gameOverScreen=document.getElementById("gameOver"),finalScoreElement=document.getElementById("finalScore"),playAgainButton=document.getElementById("playAgain"),bassDropCooldownElement=document.getElementById("bassDropCooldown");let canvasWidth=800,canvasHeight=800,scale=1;function resizeCanvas(){const container=document.getElementById("gameContainer"),containerWidth=container.clientWidth,containerHeight=container.clientHeight;scale=Math.min(containerWidth/canvasWidth,containerHeight/canvasHeight),canvas.width=canvasWidth*scale,canvas.height=canvasHeight*scale,ctx.scale(scale,scale)}window.addEventListener("resize",resizeCanvas),resizeCanvas();const TRACK_COUNT=3,TRACK_WIDTH=80,NOTE_SIZE=40,CATCH_ZONE_HEIGHT=20,TRACK_COLORS=["#FF1493","#00FFFF","#00FF7F"],NOTE_SHAPES=["circle","square","triangle"],NOTE_SPEED=5,PERFECT_THRESHOLD=30,TRACK_SPACING=(canvasWidth-TRACK_WIDTH*TRACK_COUNT)/(TRACK_COUNT+1);class Note{constructor(track,shape){this.track=track,this.y=-NOTE_SIZE,this.shape=shape,this.speed=NOTE_SPEED,this.x=TRACK_SPACING+(TRACK_WIDTH+TRACK_SPACING)*track+TRACK_WIDTH/2}update(){this.y+=this.speed}draw(){const x=this.x,y=this.y;ctx.fillStyle=TRACK_COLORS[this.track],ctx.strokeStyle=TRACK_COLORS[this.track],"circle"===this.shape?(ctx.beginPath(),ctx.arc(x,y,NOTE_SIZE/2,0,2*Math.PI),ctx.fill()):"square"===this.shape?ctx.fillRect(x-NOTE_SIZE/2,y-NOTE_SIZE/2,NOTE_SIZE,NOTE_SIZE):(ctx.beginPath(),ctx.moveTo(x,y-NOTE_SIZE/2),ctx.lineTo(x+NOTE_SIZE/2,y+NOTE_SIZE/2),ctx.lineTo(x-NOTE_SIZE/2,y+NOTE_SIZE/2),ctx.closePath(),ctx.fill())}}class DisruptionWave{constructor(){this.x=-100,this.speed=3*Math.random()+2,this.amplitude=30,this.frequency=.05}update(){this.x+=this.speed}draw(){ctx.strokeStyle="rgba(255,0,255,0.3)",ctx.beginPath();for(let y=0;y<canvasHeight;y+=20)ctx.lineTo(this.x+Math.sin(y*this.frequency)*this.amplitude,y);ctx.stroke()}}class Game{constructor(){this.notes=[],this.waves=[],this.score=0,this.combo=0,this.multiplier=1,this.missedNotes=0,this.consecutiveMisses=0,this.lastNoteTime=0,this.nextWaveTime=0,this.pulsePhase=0,this.bassDropActive=!1,this.bassDropCooldown=0,this.gameOver=!1,this.effects=[]}spawnNote(){Date.now()-this.lastNoteTime>1e3&&(this.notes.push(new Note(Math.floor(Math.random()*TRACK_COUNT),NOTE_SHAPES[Math.floor(Math.random()*NOTE_SHAPES.length)])),this.lastNoteTime=Date.now())}spawnWave(){Date.now()-this.nextWaveTime>3e3&&(this.waves.push(new DisruptionWave),this.nextWaveTime=Date.now())}addEffect(x,y,success){for(let i=0;i<3;i++)this.effects.push({x:x,y:y,radius:0,maxRadius:150+50*i,speed:8+2*i,success:success,alpha:1})}updateEffects(){this.effects=this.effects.filter(e=>(e.radius+=e.speed,e.alpha=Math.max(0,1-e.radius/e.maxRadius),e.alpha>0))}drawEffects(){this.effects.forEach(e=>{const color=e.success?`rgba(0,255,255,${e.alpha})`:`rgba(255,0,0,${e.alpha})`;ctx.strokeStyle=color,ctx.lineWidth=3,ctx.beginPath(),ctx.arc(e.x,e.y,e.radius,0,2*Math.PI),ctx.stroke(),ctx.lineWidth=1})}drawBackground(){ctx.fillStyle="#000033",ctx.fillRect(0,0,canvasWidth,canvasHeight);const gridSize=50,intensity=.3+.1*Math.sin(this.pulsePhase);ctx.strokeStyle=`rgba(0,255,255,${intensity})`;for(let x=0;x<canvasWidth;x+=gridSize)ctx.beginPath(),ctx.moveTo(x,0),ctx.lineTo(x,canvasHeight),ctx.stroke();for(let y=0;y<canvasHeight;y+=gridSize)ctx.beginPath(),ctx.moveTo(0,y),ctx.lineTo(canvasWidth,y),ctx.stroke()}drawTracks(){for(let i=0;i<TRACK_COUNT;i++){const x=TRACK_SPACING+(TRACK_WIDTH+TRACK_SPACING)*i;ctx.fillStyle=`rgba(${0===i?"255,20,147":1===i?"0,255,255":"0,255,127"},0.2)`,ctx.fillRect(x,0,TRACK_WIDTH,canvasHeight),ctx.fillStyle=TRACK_COLORS[i],ctx.fillRect(x,canvasHeight-CATCH_ZONE_HEIGHT,TRACK_WIDTH,CATCH_ZONE_HEIGHT)}}update(){this.gameOver||(this.pulsePhase+=.05,this.bassDropCooldown>0&&this.bassDropCooldown--,this.spawnNote(),this.spawnWave(),this.notes.forEach(n=>n.update()),this.waves=this.waves.filter(w=>(w.update(),w.x<canvasWidth)),this.notes=this.notes.filter(n=>n.y>canvasHeight?(this.consecutiveMisses++,this.combo=0,this.multiplier=1,this.consecutiveMisses>=3&&this.endGame(),!1):!0),this.updateEffects())}draw(){this.drawBackground(),this.drawTracks(),this.notes.forEach(n=>n.draw()),this.waves.forEach(w=>w.draw()),this.drawEffects()}checkNote(track){const catchY=canvasHeight-CATCH_ZONE_HEIGHT,note=this.notes.find(n=>n.track===track&&Math.abs(n.y-catchY)<PERFECT_THRESHOLD);if(note){Math.abs(note.y-catchY)<PERFECT_THRESHOLD&&(this.score+=100*this.multiplier,this.combo++,this.multiplier=1+Math.floor(this.combo/10),this.consecutiveMisses=0,this.addEffect(note.x,catchY,!0),this.notes=this.notes.filter(n=>n!==note))}}activateBassDropp(){0===this.bassDropCooldown&&(this.bassDropActive=!0,this.notes.forEach(n=>n.speed=NOTE_SPEED/2),this.waves.forEach(w=>w.speed/=2),setTimeout(()=>{this.bassDropActive=!1,this.notes.forEach(n=>n.speed=NOTE_SPEED),this.waves.forEach(w=>w.speed*=2)},5e3),this.bassDropCooldown=1800)}endGame(){this.gameOver=!0,finalScoreElement.textContent=this.score,gameOverScreen.style.display="flex"}reset(){this.notes=[],this.waves=[],this.score=0,this.combo=0,this.multiplier=1,this.consecutiveMisses=0,this.missedNotes=0,this.lastNoteTime=0,this.nextWaveTime=0,this.pulsePhase=0,this.bassDropActive=!1,this.bassDropCooldown=0,this.gameOver=!1,this.effects=[],gameOverScreen.style.display="none"}}const game=new Game;function gameLoop(){game.gameOver||(game.update(),game.draw(),scoreElement.textContent=`Score: ${game.score}`,comboElement.textContent=`Combo: ${game.combo}x${game.multiplier}`,bassDropCooldownElement.textContent=game.bassDropCooldown>0?`Bass Drop: ${Math.ceil(game.bassDropCooldown/60)}s`:"Bass Drop Ready",requestAnimationFrame(gameLoop))}document.addEventListener("keydown",e=>{"KeyA"===e.code||"KeyS"===e.code||"KeyD"===e.code||"Space"===e.code?(e.preventDefault(),"KeyA"===e.code?game.checkNote(0):"KeyS"===e.code?game.checkNote(1):"KeyD"===e.code?game.checkNote(2):"Space"===e.code&&game.activateBassDropp()):void 0}),playAgainButton.addEventListener("click",()=>{game.reset(),gameLoop()}),gameLoop();",
                        "language": "javascript"
                    },
                    {
                        "filename": "index.html",
                        "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width,initial-scale=1.0" /><title>Beat Match Master</title><style>body,html{margin:0;padding:0;height:100%;overflow:hidden;font-family:"Segoe UI","Helvetica Neue",Arial,sans-serif;background:#000}#gameContainer{position:relative;width:100vmin;height:100vmin;margin:auto}#gameCanvas{position:absolute;top:0;left:0;width:100%;height:100%}#hud{position:absolute;top:10px;left:10px;right:10px;display:flex;justify-content:space-between;color:#00ff00;font-size:24px;font-family:"Segoe UI","Helvetica Neue",Arial,sans-serif;text-shadow:0 0 10px #00ff00}#gameOver{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,0.9);color:#00ff00;padding:20px;border-radius:10px;text-align:center;display:none;flex-direction:column;align-items:center;font-family:"Segoe UI","Helvetica Neue",Arial,sans-serif;text-shadow:0 0 10px #00ff00}#playAgain{margin-top:20px;padding:10px 20px;font-size:18px;background:#00ff00;color:black;border:none;border-radius:5px;cursor:pointer;font-family:"Segoe UI","Helvetica Neue",Arial,sans-serif}#playAgain:hover{background:#00cc00}#controls{position:absolute;top:40px;left:50%;transform:translateX(-50%);color:#00ff00;font-size:14px;text-align:center;text-shadow:0 0 5px #00ff00}</style></head><body><div id="gameContainer"><canvas id="gameCanvas"></canvas><div id="hud"><span id="score">Score: 0</span><span id="combo">Combo: 0x1</span><span id="bassDropCooldown">Bass Drop Ready</span></div><div id="gameOver"><h2>Game Over</h2><p>Final Score: <span id="finalScore">0</span></p><button id="playAgain">Play Again</button></div><div id="controls">A/S/D - Catch Notes | SPACE - Activate Bass Drop</div></div><script src="index.js"></script></body></html>",
                        "language": "html"
                    }
                ]
            }
        </example_output_5>
    """
    examples = [example_1, example_2, example_3, example_4, example_5]
    selection = random.sample(examples, k=2)
    return "".join(selection)


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
        <example_input_3>
            Generate a self-contained coding problem that requires the programmer to implement a fun, streamlined, hyper-casual web game with 2 user actions for the following persona: A delivery driver who frequently struggles to find parking while making deliveries.
        </example_input_3>
        <example_output_3>
            Implement a fun web game called 'Perfect Park' where players must skillfully maneuver a delivery van into increasingly challenging parking spots while racing against time.

            Features:
            - Create a 2D game area representing a street view with multiple parking spots.
            - Display a delivery van sprite that can be controlled by the player.
            - Implement smooth van movement using arrow keys, with realistic turning mechanics. Ensure default key behaviors are disabled.
            - Create visual parking spot boundaries using dashed lines.
            - Add randomly placed obstacles (other parked cars, trash bins, construction cones) that the van must avoid.
            - Display a timer counting down from 60 seconds.
            - Implement a scoring system: +100 points for perfect parking (van completely within spot lines), +50 for acceptable parking (majority of van within lines).
            - Show a parking guide overlay when the van is near a valid parking spot, indicating if the current position would result in perfect or acceptable parking.
            - Add visual feedback when the van collides with obstacles (flashing red).
            - Create a 'delivery complete' animation when successfully parked (brief celebration effect).
            - Display current score and high score at the top of the screen.
            - Show 'Game Over' screen when timer reaches zero, displaying final score and 'Play Again' button.
            - Generate new obstacle layouts each time the player successfully parks or starts a new game.

            User Actions:
            1. Use arrow keys to control the delivery van (Up/Down for forward/reverse, Left/Right for steering).
            2. Press Spacebar to 'lock in' your parking attempt when you think you're properly parked. If successful, gain points and move to next layout. If unsuccessful, lose 5 seconds from the timer.
        </example_output_3>
        <example_input_4>
            Generate a self-contained coding problem that requires the programmer to implement a fun, streamlined, hyper-casual web game with 2 user actions for the following persona: A reformed hacker now working as a confidential informant, assisting in identifying and tracking down other hackers
        </example_input_4>
        <example_output_4>
            Implement a fun, streamlined web game called 'Cyberspace Conquest' where the player navigates through cyberspace and defends against enemy malware.

            Features:
            - Create a 2D game area with a neon grid that scrolls horizontally in the background to represent cyberspace.
            - The game area must wrap around all edges (malware and players that go off one side appear on the opposite side).
            - The player controls a triangular hacker sprite to navigate through cyberspace. Player movement should resemble a spaceship.
            - The player must fire projectiles (maximum of 5 at one time) at enemy malware. The projectiles should travel a finite distance before disappearing.
            - Create enemy malware as irregular polygons that drift through cyberspace. The malware should move in straight lines at different angles and speeds.
            - When malware is hit by the player's projectiles, it should split into smaller malware, and the player's score should increase.
            - The player has 3 lives. If the player collides with malware, the player should lose a life, and become briefly invulnerable, before respawning at the center of the screen.
            - Show a game over screen when the player loses all their lives, showing the final score and a 'Play Again' button.
            - The game should display the player's score, high score and lives on the screen.
            - Use a cyberpunk colour scheme and aesthetic (deep purple as the background, neon pink for the HUD).

            User Actions:
            1. Use the arrow keys to navigate through cyberspace.
            2. Press the spacebar to fire projectiles at enemy malware.
        </example_output_4>
        <example_input_5>
            Generate a self-contained coding problem that requires the programmer to implement a fun, streamlined, hyper-casual web game with 2 user actions for the following persona: A seasoned DJ with decades of experience in the club scene and a vast knowledge of techno and house music.
        </example_input_5>
        <example_output_5>
            Implement a fun web game called "Beat Match Master" where players must catch falling music notes by clicking at the right moment while avoiding disruptive elements.

            Features:
            - Create a vertical game area with a neon grid background that pulses to a constant rhythm (60 BPM).
            - Display three vertical "track lines" where notes can fall, colored in distinct neon colors (pink, cyan, green).
            - Generate music notes that fall down these track lines at a constant speed. The notes should be simple geometric shapes (circles, squares, triangles).
            - Each note should have a "perfect catch zone" at the bottom of its track line, visualized as a thin horizontal line.
            - Create visual feedback when notes are caught: successful catches create expanding rings of light, while misses create a brief static effect.
            - Add "disruption waves" that periodically move horizontally across the screen. These waves should be visually distinct (zigzag patterns) and move at varying speeds.
            - Display a score multiplier that increases with consecutive successful catches and resets on misses.
            - Show the current score prominently at the top of the screen with a retro digital display aesthetic.
            - Create a combo counter that tracks successive successful catches.
            - Add visual effects that intensify as the combo counter increases (background pulse becomes stronger, colors become more vibrant).
            - When the player reaches certain score thresholds, increase the speed and frequency of falling notes.
            - Display a "Game Over" screen when three consecutive notes are missed, showing final score and a "Play Again" button.
            - The game's color scheme should use bright neon colors against a dark background to create a club atmosphere.

            User Actions:
            1. Press the A, S, or D keys to catch notes in the left, middle, or right tracks respectively when they align with the catch zone.
            2. Press the spacebar to activate "Bass Drop" which slows down all notes and waves for 5 seconds (can be used once every 30 seconds).
        </example_output_5>
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
        Generate a self-contained coding problem that requires the programmer to implement a streamlined, interactive simulation with 2 user actions for the following persona: "A renowned snooker historian specializing in the origins and development of the game".
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
    <example_input_3>
        Generate a self-contained coding problem that requires the programmer to implement a streamlined, interactive simulation with 3 user actions for the following persona: "a military strategist who has served in the Indian Army for over 20 years."
    </example_input_3>
    <example_output_3>
       Create an interactive particle simulation demonstrating the principles of projectile motion and gravitational effects in a military-themed environment.

        Features:
        - Create a side-view scene with a desert landscape background using CSS gradients.
        - Display a launching platform (styled as a military bunker) on the left side of the screen.
        - Implement a targeting system with a visible trajectory arc that updates in real-time as the user adjusts launch parameters.
        - Create particles that follow realistic projectile motion physics, accounting for initial velocity, angle, and gravity.
        - Display real-time data panel showing:
        * Current projectile velocity
        * Launch angle
        * Maximum height reached
        * Wind direction and speed
        - Create three targets on the right side of the screen. When all three targets are hit, they should respawn in new positons.
        - Implement a wind effect and change the wind direction and speed after each launch.
        - Add visual effects for particle launches (small explosion animation at launch).
        - Include particle trail effects that fade over time.
        - Display a score counter for successful target hits.
        - Create a reset button styled as a military command button.

        User Actions:
        1. Use the left/right arrow keys to adjust the launch angle (0-90 degrees). A visual indicator should show the current angle.
        2. Use the up/down arrow keys to adjust the initial launch velocity (shown as a power meter on screen).
        3. Press the spacebar to launch a particle, which will follow the calculated trajectory while being affected by gravity and wind.
    </example_output_3>
    <example_input_4>
        Generate a self-contained coding problem that requires the programmer to implement a streamlined, interactive simulation with 2 user actions for the following persona: A conscientious citizen committed to carefully evaluating evidence and delivering a fair verdict.
    </example_input_4>
    <example_output_4>
        Create an interactive particle-based jury deliberation simulation that demonstrates the principles of social influence and consensus-building through a physics-based visualization.

        Features:
        - Create a circular deliberation chamber using CSS, styled with a formal courthouse aesthetic (wood textures and neutral colors).
        - Display 12 particle entities representing jurors, each as a circular element with a unique identifier.
        - Each juror particle should have a color gradient representing their current verdict stance (red for guilty, green for not guilty).
        - Implement a physics system where particles can:
        * Move continuously and freely within the chamber bounds
        * Collide elastically with chamber walls and other particles
        * Generate subtle connection lines between nearby particles
        - Create an influence radius around each particle, visualized as a semi-transparent circle.
        - When particle influence radiuses overlap, their colors should influence each other based on proximity and duration of contact.
        - Display a real-time statistics panel showing:
        * Current distribution of verdicts
        * Time elapsed in deliberation
        * Number of significant interactions (when particles stay in proximity for over 3 seconds)
        - Add visual effects for particle interactions (subtle glow when particles influence each other).
        - Create a reset button styled as a formal gavel icon.

        User Actions:
        1. Click and drag individual particles to manually position them, simulating directed jury interactions.
        2. Right-click any particle to temporarily lock its opinion, preventing it from being influenced by others (simulating a strongly convinced juror).
    </example_output_4>
    <example_input_5>
        Generate a self-contained coding problem that requires the programmer to implement a streamlined, interactive simulation with 2 user actions for the following persona: A recreational amateur astronomer with only a basic telescope.
    </example_input_5>
    <example_output_5>
        Create an interactive orbital mechanics simulation that demonstrates Kepler's Laws of Planetary Motion through a simplified 2D visualization of a solar system.

        Features:
        - Create a dark space background with a subtle star field effect using CSS.
        - Display a central star (sun) in the center of the screen using gradients to create a glowing effect.
        - Create a movable planet that orbits the central star following Kepler's First Law (elliptical orbit).
        - Implement simplified gravitational physics where:
        * The planet's velocity changes based on its distance from the star (demonstrating Kepler's Second Law)
        * The orbit's period is mathematically related to its semi-major axis (demonstrating Kepler's Third Law)
        - Display a faint elliptical orbit line that updates in real-time as orbital parameters change.
        - Show a real-time data panel styled as a telescope display interface, containing:
        * Current orbital period
        * Current velocity
        * Distance from star
        * Orbital eccentricity
        - Create orbital trail effects that fade over time, showing the planet's recent path.
        - Add visual effects for the planet (subtle glow based on its proximity to the star).
        - Implement a "telescopic view" aesthetic with circular vignette corners and grid lines.
        - Include a reset button styled as a telescope adjustment knob.

        User Actions:
        1. Click and drag anywhere on the orbital path to adjust its shape and size. The ellipse should deform smoothly following the mouse, while maintaining the star at one focus (demonstrating Kepler's First Law). The planet's motion should automatically adjust to the new orbital parameters.
        2. Press and hold the spacebar to enter "time warp" mode, increasing the simulation speed to better observe long-term orbital behavior. Release to return to normal speed.
    </example_output_5>
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
            Generate a self-contained coding problem that requires the programmer to implement a interactive visualization with 2 user actions for the following persona: A competitive archer and fellow instructor who constantly challenges and pushes the instructor to improve their skills.
        </example_input_2>
        <example_output_2>
            Create an interactive archery target practice simulator that visualizes different arrow trajectories on an archery range.

            Features:
            - Display a side-view archery range with a regulation height target (4 feet center)
            - Implement an arrow that can be launched with different trajectories
            - When the arrow is launched, it should follow a parabolic arc according to basic physics principles
            - Include a power meter that fills up while the user holds down the mouse button, determining the arrow's initial velocity
            - The angle of the shot should be determined by the vertical position of the mouse cursor when releasing the button.
            - Display a real-time arc angle indicator that updates as the user moves their mouse vertically. The angle of the shot should be displayed in degrees next to the arrow.
            - When the arrow reaches the target, provide visual feedback:
            * Green hit marker effect for shots that hit the target.
            * Red hit marker effect for shots that miss the target.
            - Keep track and display the current accuracy percentage.
            - The target should have realistic scoring rings that the arrow can stick into.
            - Implement a simple animation when the arrow embeds into the target.
            - Reset the arrow to its starting position after each shot. Successful shots should remain in the target.

            User Actions:
            1. Press and hold the mouse button to draw the bow and charge the power meter, then release to shoot.
            2. Move the mouse cursor up and down to adjust the angle of the shot.

            Note: This visualization draws inspiration from archery mechanics, particularly the importance of arc in arrow trajectory, which is fundamental to competitive archery techniques.
        </example_output_2>
        <example_input_3>
            Generate a self-contained coding problem that requires the programmer to implement a interactive visualization with 3 user actions for the following persona: a retired professional cheerleader who has participated in various international competitions.
        </example_input_3>
        <example_output_3>
            Create an interactive pom-pom trail visualization that responds to mouse movement and user controls.

            Features:
            - Display a trail of colorful circular pom-poms that follow the user's mouse cursor across the screen
            - Each pom-pom should be represented by a cluster of small circles arranged in a circular pattern to create a fluffy appearance
            - The trail should consist of at least 20 pom-poms that follow the mouse cursor with a slight delay, creating a smooth, wave-like motion
            - Implement a color-cycling animation for the pom-poms, transitioning through a preset palette of vibrant colors
            - Add a particle effect that emanates from each pom-pom when the user clicks, simulating sparkles or confetti
            - Include a control panel with:
            * A slider to adjust the length of the pom-pom trail (from 10 to 30 pom-poms)
            * A color picker that sets the base color scheme for the pom-poms
            * A button to toggle between smooth and bouncy movement patterns
            - When movement pattern is set to "bouncy", the pom-poms should follow the cursor with an energetic, spring-like motion

            User Actions:
            1. Move the mouse cursor to control the pom-pom trail's position and create dynamic patterns
            2. Click anywhere on the screen to trigger a burst of sparkle particles from each pom-pom in the trail
            3. Use the control panel to:
            - Adjust the trail length using the slider
            - Select different color schemes using the color picker
            - Toggle between smooth and bouncy movement patterns using the button
        </example_output_3>
        <example_input_4>
        Generate a self-contained coding problem that requires the programmer to implement a interactive visualization with 2 user actions for the following persona: A young artist eager to learn the techniques and secrets of weaving intricate patterns.
        </example_input_4>
        <example_output_4>
            Create an interactive pattern weaver that generates mesmerizing kaleidoscopic designs using HTML, CSS, and JavaScript.

            Features:
            - Display a circular canvas where patterns are generated in real-time as the user moves their mouse.
            - The pattern should be symmetrically mirrored across multiple axes to create a kaleidoscope effect.
            - Implement at least 8 mirror segments that reflect the user's drawing motions.
            - As the user moves their mouse within the canvas, colorful lines should be drawn that create flowing, continuous patterns.
            - The lines should have a smooth, gradient-like color transition that shifts through the rainbow spectrum.
            - The thickness of the lines should vary based on the mouse movement speed - faster movements create thinner lines, slower movements create thicker lines.
            - Include a color palette selector that allows users to choose between different color schemes (e.g., warm colors, cool colors, pastels).
            - Add a 'clear canvas' button that smoothly fades out the existing pattern and resets the canvas.
            - The entire pattern should slowly rotate continuously, creating an animated effect.

            User Actions:
            1. Move the mouse within the circular canvas to draw symmetrical patterns. The pattern will be automatically mirrored across all segments in real-time.
            2. Click a button to cycle through different color schemes for the pattern lines. Each click should smoothly transition the existing pattern to the new color scheme.
        </example_output_4>
        <example_input_5>
            Generate a self-contained coding problem that requires the programmer to implement a interactive visualization with 2 user actions for the following persona: A soccer coach who is passionately nationalistic about Portugal's football team and often overly optimistic about their performance on the world stage.
        </example_input_5>
        <example_output_5>
            Create an interactive soccer field visualization that simulates Portugal's dynamic passing patterns.

            Features:
            - Display a top-down view of a soccer field with standard field markings (lines, center circle, penalty boxes) using HTML canvas.
            - Show 11 red circular nodes representing Portugal's players positioned in a 4-3-3 formation.
            - Each player node should have a small Portuguese flag element above it.
            - Implement an animated passing sequence where a glowing ball travels between player nodes along curved paths.
            - The passing lines should be drawn with a trailing effect in Portugal's national colors (red and green).
            - The ball's movement should have smooth acceleration and deceleration between passes.
            - Display a "Pass Completion Rate" counter at the top of the screen that starts at 100%.
            - Include a speed control slider that adjusts how fast the passing sequence occurs.
            - Implement a user controlled defender that can intercept the ball.
            - When passes fail (when the defender intercepts the ball), the passing and receiving player nodes should briefly flash in a darker shade.
            - The passing sequence should continuously loop, only briefly stopping after an interception.
            - Each player node should slowly oscillate to mimic off the ball movement.

            User Actions:
            1. Use the arrow keys to control the defender. Successfully intercepting the ball will:
            - Cause the current pass to fail
            - Decrease the "Pass Completion Rate" by 5%
            - Create a brief visual disruption effect on the passing line
            2. Use a slider control to adjust the speed of the passing sequence from slow (tactical analysis speed) to fast (match speed).
        </example_output_5>
        """


def _get_animation_answer_examples() -> str:
    example_1 = """
    <example_input_1>
        Create an interactive archery target practice simulator that visualizes different arrow trajectories on an archery range.

        Features:
        - Display a side-view archery range with a regulation height target (4 feet center)
        - Implement an arrow that can be launched with different trajectories
        - When the arrow is launched, it should follow a parabolic arc according to basic physics principles
        - Include a power meter that fills up while the user holds down the mouse button, determining the arrow's initial velocity
        - The angle of the shot should be determined by the vertical position of the mouse cursor when releasing the button.
        - Display a real-time arc angle indicator that updates as the user moves their mouse vertically. The angle of the shot should be displayed in degrees next to the arrow.
        - When the arrow reaches the target, provide visual feedback:
        * Green hit marker effect for shots that hit the target.
        * Red hit marker effect for shots that miss the target.
        - Keep track and display the current accuracy percentage.
        - The target should have realistic scoring rings that the arrow can stick into.
        - Implement a simple animation when the arrow embeds into the target.
        - Reset the arrow to its starting position after each shot. Successful shots should remain in the target.

        User Actions:
        1. Press and hold the mouse button to draw the bow and charge the power meter, then release to shoot.
        2. Move the mouse cursor up and down to adjust the angle of the shot.

        Note: This visualization draws inspiration from archery mechanics, particularly the importance of arc in arrow trajectory, which is fundamental to competitive archery techniques.
    </example_input_1>
    <example_output_1>
        {
        "files": [
            {
                "filename": "index.js",
                "content": "const canvas=document.getElementById("canvas"),ctx=canvas.getContext("2d"),stats=document.getElementById("stats"),width=canvas.width=800,height=canvas.height=600,targetX=width-100,targetY=height-240,targetRadius=60,rings=[{radius:60,color:"#FFFFFF",points:1},{radius:48,color:"#000000",points:2},{radius:36,color:"#1E90FF",points:3},{radius:24,color:"#FF0000",points:4},{radius:12,color:"#FFD700",points:5}];let power=0,isCharging=!1,angle=0,arrowX=100,arrowY=height-100,arrowVelX=0,arrowVelY=0,isFlying=!1,shots=0,hits=0,arrows=[],hitAnimations=[];function drawTarget(){rings.forEach(e=>{ctx.beginPath(),ctx.arc(targetX,targetY,e.radius,0,2*Math.PI),ctx.fillStyle=e.color,ctx.fill(),ctx.stroke()})}function drawPowerMeter(){ctx.fillStyle="rgba(0,0,0,0.5)",ctx.fillRect(50,height-30,100,20),ctx.fillStyle=`rgb(${255*power/100}, ${255*(1-power/100)}, 0)`,ctx.fillRect(50,height-30,power,20)}function drawAngleIndicator(){ctx.save(),ctx.translate(arrowX,arrowY),ctx.rotate(-angle),ctx.beginPath(),ctx.moveTo(0,0),ctx.lineTo(50,0),ctx.strokeStyle="rgba(255,255,255,0.5)",ctx.setLineDash([5,5]),ctx.stroke(),ctx.setLineDash([]),ctx.rotate(angle),ctx.fillStyle="white",ctx.font="16px Arial";const e=Math.round(180*angle/Math.PI);ctx.fillText(`${e}°`,60,0),ctx.restore()}function drawArrow(e,t,r){ctx.save(),ctx.translate(e,t),ctx.rotate(r),ctx.beginPath(),ctx.moveTo(-20,0),ctx.lineTo(20,0),ctx.strokeStyle="#8B4513",ctx.lineWidth=3,ctx.stroke(),ctx.beginPath(),ctx.moveTo(20,0),ctx.lineTo(15,-5),ctx.lineTo(15,5),ctx.fillStyle="#A0522D",ctx.fill(),ctx.beginPath(),ctx.moveTo(-20,0),ctx.lineTo(-15,-5),ctx.lineTo(-10,0),ctx.lineTo(-15,5),ctx.fillStyle="#FF0000",ctx.fill(),ctx.restore()}function updateArrow(){if(isFlying){arrowVelY+=.5,arrowX+=arrowVelX,arrowY+=arrowVelY;const e=arrowX-targetX,t=arrowY-targetY,r=Math.sqrt(e*e+t*t);if(r<targetRadius){isFlying=!1,shots++;let e=0;for(let t=rings.length-1;t>=0;t--)if(r<=rings[t].radius){e=rings[t].points;break}hits++,arrows.push({x:arrowX,y:arrowY,rotation:Math.atan2(arrowVelY,arrowVelX)}),hitAnimations.push({x:arrowX,y:arrowY,radius:0,opacity:.8,color:"#00ff00"}),resetArrow()}arrowY>height-20&&(shots++,hitAnimations.push({x:arrowX,y:arrowY,radius:0,opacity:.8,color:"#ff0000"}),resetArrow())}}function resetArrow(){arrowX=100,arrowY=height-100,arrowVelX=0,arrowVelY=0,isFlying=!1,power=0,updateStats()}function updateStats(){const e=0===shots?0:Math.round(hits/shots*100);stats.textContent=`Shots: ${shots} | Hits: ${hits} | Accuracy: ${e}%`}function draw(){ctx.clearRect(0,0,width,height),ctx.fillStyle="#8b7355",ctx.fillRect(0,height-40,width,40),drawTarget(),arrows.forEach(e=>{drawArrow(e.x,e.y,e.rotation)}),isFlying||(drawPowerMeter(),drawAngleIndicator()),isFlying?drawArrow(arrowX,arrowY,Math.atan2(arrowVelY,arrowVelX)):drawArrow(arrowX,arrowY,-angle),updateArrow(),updateHitAnimations(),requestAnimationFrame(draw)}function updatePower(){isCharging&&!isFlying&&(power=Math.min(100,power+2)),setTimeout(updatePower,20)}function updateHitAnimations(){hitAnimations=hitAnimations.filter(e=>(ctx.beginPath(),ctx.arc(e.x,e.y,e.radius,0,2*Math.PI),ctx.strokeStyle=`${e.color}${Math.floor(255*e.opacity).toString(16).padStart(2,"0")}`,ctx.lineWidth=3,ctx.stroke(),e.radius+=2,e.opacity-=.02,e.opacity>0))}canvas.addEventListener("mousedown",e=>{isFlying||(isCharging=!0)}),canvas.addEventListener("mousemove",e=>{if(!isFlying){const t=canvas.getBoundingClientRect(),r=e.clientY-t.top;angle=Math.max(0,Math.min(Math.PI/2,(height-r)/height*Math.PI))}}),canvas.addEventListener("mouseup",e=>{isCharging&&!isFlying&&(isCharging=!1,isFlying=!0,arrowVelX=.2*power*Math.cos(-angle),arrowVelY=.2*power*Math.sin(-angle))}),window.addEventListener("keydown",e=>{"Space"===e.code&&e.preventDefault()}),window.addEventListener("resize",()=>{width=canvas.width=Math.min(800,window.innerWidth),height=canvas.height=Math.min(600,window.innerHeight)}),updatePower(),draw();",
                "language": "javascript"
            },
            {
                "filename": "index.html",
                "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/><title>Archery Practice Simulator</title><style>body{margin:0;overflow:hidden;background:#2c3e50;display:flex;justify-content:center;align-items:center;height:100vh;font-family:Arial,sans-serif}#canvas{background:linear-gradient(180deg,#87ceeb 0%,#87ceeb 60%,#8b7355 60%,#8b7355 100%)}#stats{position:fixed;top:10px;left:10px;color:white;background:rgba(0,0,0,0.5);padding:10px;border-radius:5px;font-size:14px}#instructions{position:fixed;bottom:10px;left:10px;color:white;background:rgba(0,0,0,0.5);padding:10px;border-radius:5px;font-size:14px}</style></head><body><canvas id="canvas"></canvas><div id="stats">Accuracy: 0%</div><div id="instructions">Hold mouse to charge power<br/>Release to shoot<br/>Mouse height controls angle</div><script src="index.js"></script></body></html>",
                "language": "html"
            }
            ]
        }
    </example_output_1>
    """
    example_2 = """
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
    example_3 = """
    <example_input_3>
        Create an interactive pom-pom trail visualization that responds to mouse movement and user controls.

            Features:
            - Display a trail of colorful circular pom-poms that follow the user's mouse cursor across the screen
            - Each pom-pom should be represented by a cluster of small circles arranged in a circular pattern to create a fluffy appearance
            - The trail should consist of at least 20 pom-poms that follow the mouse cursor with a slight delay, creating a smooth, wave-like motion
            - Implement a color-cycling animation for the pom-poms, transitioning through a preset palette of vibrant colors
            - Add a particle effect that emanates from each pom-pom when the user clicks, simulating sparkles or confetti
            - Include a control panel with:
            * A slider to adjust the length of the pom-pom trail (from 10 to 30 pom-poms)
            * A color picker that sets the base color scheme for the pom-poms
            * A button to toggle between smooth and bouncy movement patterns
            - When movement pattern is set to "bouncy", the pom-poms should follow the cursor with an energetic, spring-like motion

            User Actions:
            1. Move the mouse cursor to control the pom-pom trail's position and create dynamic patterns
            2. Click anywhere on the screen to trigger a burst of sparkle particles from each pom-pom in the trail
            3. Use the control panel to:
            - Adjust the trail length using the slider
            - Select different color schemes using the color picker
            - Toggle between smooth and bouncy movement patterns using the button
    </example_input_3>
    <example_output_3>
        [
            {
                "filename": "index.js",
                "content": "const canvas=document.getElementById('canvas'),ctx=canvas.getContext('2d'),lengthSlider=document.getElementById('lengthSlider'),lengthValue=document.getElementById('lengthValue'),colorPicker=document.getElementById('colorPicker'),patternToggle=document.getElementById('patternToggle');let width=canvas.width=window.innerWidth,height=canvas.height=window.innerHeight,mouseX=width/2,mouseY=height/2,isBouncy=!1,trailLength=20,baseColor=colorPicker.value;class PomPom{constructor(x,y){this.x=x,this.y=y,this.targetX=x,this.targetY=y,this.velX=0,this.velY=0,this.size=20,this.color=baseColor,this.particles=[]}update(targetX,targetY){this.targetX=targetX,this.targetY=targetY,isBouncy?(this.velX+=(this.targetX-this.x)*.1,this.velY+=(this.targetY-this.y)*.1,this.velX*=.8,this.velY*=.8,this.x+=this.velX,this.y+=this.velY):(this.x+=(this.targetX-this.x)*.2,this.y+=(this.targetY-this.y)*.2),this.particles=this.particles.filter(p=>p.life>0),this.particles.forEach(p=>{p.x+=p.vx,p.y+=p.vy,p.life-=1,p.vy+=.1})}draw(hueOffset){for(let i=0;i<12;i++){const angle=i/12*Math.PI*2,fluffX=this.x+Math.cos(angle)*(this.size*.5),fluffY=this.y+Math.sin(angle)*(this.size*.5);ctx.beginPath(),ctx.arc(fluffX,fluffY,this.size*.4,0,Math.PI*2),ctx.fillStyle=this.shiftHue(this.color,hueOffset),ctx.fill()}this.particles.forEach(p=>{ctx.beginPath(),ctx.arc(p.x,p.y,p.size,0,Math.PI*2),ctx.fillStyle=`rgba(255, 255, 255, ${p.life/50})`,ctx.fill()})}addParticles(){for(let i=0;i<10;i++)this.particles.push({x:this.x,y:this.y,vx:(Math.random()-.5)*8,vy:(Math.random()-.5)*8,size:Math.random()*3+1,life:50})}shiftHue(color,offset){const r=parseInt(color.slice(1,3),16),g=parseInt(color.slice(3,5),16),b=parseInt(color.slice(5,7),16);let[h,s,l]=rgbToHsl(r,g,b);h=(h+offset)%360;const[r2,g2,b2]=hslToRgb(h,s,l);return`rgb(${r2}, ${g2}, ${b2})`}}function rgbToHsl(r,g,b){r/=255,g/=255,b/=255;const max=Math.max(r,g,b),min=Math.min(r,g,b);let h,s,l=(max+min)/2;if(max===min)h=s=0;else{const d=max-min;s=l>.5?d/(2-max-min):d/(max+min);switch(max){case r:h=(g-b)/d+(g<b?6:0);break;case g:h=(b-r)/d+2;break;case b:h=(r-g)/d+4}h/=6}return[360*h,100*s,100*l]}function hslToRgb(h,s,l){h/=360,s/=100,l/=100;let r,g,b;if(0===s)r=g=b=l;else{const hue2rgb=(p,q,t)=>(t<0&&(t+=1),t>1&&(t-=1),t<1/6?p+6*(q-p)*t:t<.5?q:t<2/3?p+6*(q-p)*(2/3-t):p),q=l<.5?l*(1+s):l+s-l*s,p=2*l-q;r=hue2rgb(p,q,h+1/3),g=hue2rgb(p,q,h),b=hue2rgb(p,q,h-1/3)}return[Math.round(255*r),Math.round(255*g),Math.round(255*b)]}let pomPoms=[];function init(){pomPoms=[];for(let i=0;i<trailLength;i++)pomPoms.push(new PomPom(width/2,height/2))}function animate(){ctx.fillStyle='rgba(17, 17, 17, 0.1)',ctx.fillRect(0,0,width,height);let lastX=mouseX,lastY=mouseY;pomPoms.forEach((pom,index)=>{pom.update(lastX,lastY),pom.draw(index*(360/trailLength)),lastX=pom.x,lastY=pom.y}),requestAnimationFrame(animate)}canvas.addEventListener('mousemove',e=>{mouseX=e.clientX,mouseY=e.clientY}),canvas.addEventListener('click',()=>{pomPoms.forEach(pom=>pom.addParticles())}),lengthSlider.addEventListener('input',e=>{trailLength=parseInt(e.target.value),lengthValue.textContent=trailLength,init()}),colorPicker.addEventListener('input',e=>{baseColor=e.target.value,pomPoms.forEach(pom=>pom.color=baseColor)}),patternToggle.addEventListener('click',()=>{isBouncy=!isBouncy,patternToggle.textContent=isBouncy?'Toggle Smooth Mode':'Toggle Bouncy Mode'}),window.addEventListener('resize',()=>{width=canvas.width=window.innerWidth,height=canvas.height=window.innerHeight}),init(),animate();const canvas=document.getElementById('canvas'),ctx=canvas.getContext('2d'),lengthSlider=document.getElementById('lengthSlider'),lengthValue=document.getElementById('lengthValue'),colorPicker=document.getElementById('colorPicker'),patternToggle=document.getElementById('patternToggle');let width=canvas.width=window.innerWidth,height=canvas.height=window.innerHeight,mouseX=width/2,mouseY=height/2,isBouncy=!1,trailLength=20,baseColor=colorPicker.value;class PomPom{constructor(x,y){this.x=x,this.y=y,this.targetX=x,this.targetY=y,this.velX=0,this.velY=0,this.size=20,this.color=baseColor,this.particles=[]}update(targetX,targetY){this.targetX=targetX,this.targetY=targetY,isBouncy?(this.velX+=(this.targetX-this.x)*.1,this.velY+=(this.targetY-this.y)*.1,this.velX*=.8,this.velY*=.8,this.x+=this.velX,this.y+=this.velY):(this.x+=(this.targetX-this.x)*.2,this.y+=(this.targetY-this.y)*.2),this.particles=this.particles.filter(p=>p.life>0),this.particles.forEach(p=>{p.x+=p.vx,p.y+=p.vy,p.life-=1,p.vy+=.1})}draw(hueOffset){for(let i=0;i<12;i++){const angle=i/12*Math.PI*2,fluffX=this.x+Math.cos(angle)*(this.size*.5),fluffY=this.y+Math.sin(angle)*(this.size*.5);ctx.beginPath(),ctx.arc(fluffX,fluffY,this.size*.4,0,Math.PI*2),ctx.fillStyle=this.shiftHue(this.color,hueOffset),ctx.fill()}this.particles.forEach(p=>{ctx.beginPath(),ctx.arc(p.x,p.y,p.size,0,Math.PI*2),ctx.fillStyle=`rgba(255, 255, 255, ${p.life/50})`,ctx.fill()})}addParticles(){for(let i=0;i<10;i++)this.particles.push({x:this.x,y:this.y,vx:(Math.random()-.5)*8,vy:(Math.random()-.5)*8,size:Math.random()*3+1,life:50})}shiftHue(color,offset){const r=parseInt(color.slice(1,3),16),g=parseInt(color.slice(3,5),16),b=parseInt(color.slice(5,7),16);let[h,s,l]=rgbToHsl(r,g,b);h=(h+offset)%360;const[r2,g2,b2]=hslToRgb(h,s,l);return`rgb(${r2}, ${g2}, ${b2})`}}function rgbToHsl(r,g,b){r/=255,g/=255,b/=255;const max=Math.max(r,g,b),min=Math.min(r,g,b);let h,s,l=(max+min)/2;if(max===min)h=s=0;else{const d=max-min;s=l>.5?d/(2-max-min):d/(max+min);switch(max){case r:h=(g-b)/d+(g<b?6:0);break;case g:h=(b-r)/d+2;break;case b:h=(r-g)/d+4}h/=6}return[360*h,100*s,100*l]}function hslToRgb(h,s,l){h/=360,s/=100,l/=100;let r,g,b;if(0===s)r=g=b=l;else{const hue2rgb=(p,q,t)=>(t<0&&(t+=1),t>1&&(t-=1),t<1/6?p+6*(q-p)*t:t<.5?q:t<2/3?p+6*(q-p)*(2/3-t):p),q=l<.5?l*(1+s):l+s-l*s,p=2*l-q;r=hue2rgb(p,q,h+1/3),g=hue2rgb(p,q,h),b=hue2rgb(p,q,h-1/3)}return[Math.round(255*r),Math.round(255*g),Math.round(255*b)]}let pomPoms=[];function init(){pomPoms=[];for(let i=0;i<trailLength;i++)pomPoms.push(new PomPom(width/2,height/2))}function animate(){ctx.fillStyle='rgba(17, 17, 17, 0.1)',ctx.fillRect(0,0,width,height);let lastX=mouseX,lastY=mouseY;pomPoms.forEach((pom,index)=>{pom.update(lastX,lastY),pom.draw(index*(360/trailLength)),lastX=pom.x,lastY=pom.y}),requestAnimationFrame(animate)}canvas.addEventListener('mousemove',e=>{mouseX=e.clientX,mouseY=e.clientY}),canvas.addEventListener('click',()=>{pomPoms.forEach(pom=>pom.addParticles())}),lengthSlider.addEventListener('input',e=>{trailLength=parseInt(e.target.value),lengthValue.textContent=trailLength,init()}),colorPicker.addEventListener('input',e=>{baseColor=e.target.value,pomPoms.forEach(pom=>pom.color=baseColor)}),patternToggle.addEventListener('click',()=>{isBouncy=!isBouncy,patternToggle.textContent=isBouncy?'Toggle Smooth Mode':'Toggle Bouncy Mode'}),window.addEventListener('resize',()=>{width=canvas.width=window.innerWidth,height=canvas.height=window.innerHeight}),init(),animate();",
                "language": "javascript"
            },
            {
                "filename": "index.html",
                "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><title>Interactive Pom-Pom Trail</title><style>body{margin:0;overflow:hidden;background-color:#111;font-family:Arial,sans-serif}.controls{position:fixed;bottom:20px;left:20px;background:rgba(0,0,0,0.7);padding:15px;border-radius:10px;color:#fff;z-index:100}.controls label{display:block;margin:5px 0}.controls input[type="range"]{width:150px}.controls button{background:#444;color:#fff;border:none;padding:8px 15px;border-radius:5px;cursor:pointer;margin-top:5px}.controls button:hover{background:#666}</style></head><body><div class="controls"><label>Trail Length: <span id="lengthValue">20</span><input type="range" id="lengthSlider" min="10" max="30" value="20" /></label><label>Base Color: <input type="color" id="colorPicker" value="#ff4488" /></label><button id="patternToggle">Toggle Bouncy Mode</button></div><canvas id="canvas"></canvas><script src="index.js"></script></body></html>",
                "language": "html"
            }
        ]
    </example_output_3>
    """
    example_4 = """
    <example_input_4>
        Create an interactive pattern weaver that generates mesmerizing kaleidoscopic designs using HTML, CSS, and JavaScript.

        Features:
        - Display a circular canvas where patterns are generated in real-time as the user moves their mouse.
        - The pattern should be symmetrically mirrored across multiple axes to create a kaleidoscope effect.
        - Implement at least 8 mirror segments that reflect the user's drawing motions.
        - As the user moves their mouse within the canvas, colorful lines should be drawn that create flowing, continuous patterns.
        - The lines should have a smooth, gradient-like color transition that shifts through the rainbow spectrum.
        - The thickness of the lines should vary based on the mouse movement speed - faster movements create thinner lines, slower movements create thicker lines.
        - Include a color palette selector that allows users to choose between different color schemes (e.g., warm colors, cool colors, pastels).
        - Add a 'clear canvas' button that smoothly fades out the existing pattern and resets the canvas.
        - The entire pattern should slowly rotate continuously, creating an animated effect.

        User Actions:
        1. Move the mouse within the circular canvas to draw symmetrical patterns. The pattern will be automatically mirrored across all segments in real-time.
        2. Click a button to cycle through different color schemes for the pattern lines. Each click should smoothly transition the existing pattern to the new color scheme.
    </example_input_4>
    <example_output_4>
        [
            {
                "filename": "index.js",
                "content": "const canvas=document.getElementById('canvas'),ctx=canvas.getContext('2d'),colorSchemeBtn=document.getElementById('colorScheme'),clearBtn=document.getElementById('clear'),colorSchemes=[['#FF6B6B','#4ECDC4','#45B7D1','#96CEB4','#FFEEAD'],['#264653','#2A9D8F','#E9C46A','#F4A261','#E76F51'],['#BDE0FE','#A2D2FF','#CDB4DB','#FFC8DD','#FFAFCC'],['#390099','#9E0059','#FF0054','#FF5400','#FFBD00']];let width=canvas.width=Math.min(window.innerWidth,window.innerHeight)*.8,height=canvas.height=width,centerX=width/2,centerY=height/2,rotation=0,lastX=0,lastY=0,isDrawing=!1,currentSchemeIndex=0,currentColorIndex=0;function getColor(){const e=colorSchemes[currentSchemeIndex];return currentColorIndex=(currentColorIndex+1)%e.length,e[currentColorIndex]}function drawSegment(e,t,n,r,i=8){const o=2*Math.PI/i,a=getColor(),s=Math.sqrt(Math.pow(n-e,2)+Math.pow(r-t,2)),c=Math.max(1,10-.1*s);ctx.lineWidth=c,ctx.strokeStyle=a,ctx.lineCap='round';for(let a=0;a<i;a++){ctx.save(),ctx.translate(centerX,centerY),ctx.rotate(o*a+rotation);const i=e-centerX,s=t-centerY,c=n-centerX,l=r-centerY;ctx.beginPath(),ctx.moveTo(i,s),ctx.lineTo(c,l),ctx.stroke(),ctx.scale(-1,1),ctx.beginPath(),ctx.moveTo(i,s),ctx.lineTo(c,l),ctx.stroke(),ctx.restore()}}function animate(){rotation+=.001,requestAnimationFrame(animate)}function handleMouseMove(e){if(!isDrawing)return;const t=canvas.getBoundingClientRect(),n=e.clientX-t.left,r=e.clientY-t.top;Math.sqrt(Math.pow(n-centerX,2)+Math.pow(r-centerY,2))<=width/2&&drawSegment(lastX,lastY,n,r),lastX=n,lastY=r}function handleMouseDown(e){isDrawing=!0;const t=canvas.getBoundingClientRect();lastX=e.clientX-t.left,lastY=e.clientY-t.top}function handleMouseUp(){isDrawing=!1}function changeColorScheme(){currentSchemeIndex=(currentSchemeIndex+1)%colorSchemes.length}function clearCanvas(){ctx.fillStyle='rgba(0, 0, 0, 0.1)';!function e(){ctx.fillRect(0,0,width,height),ctx.globalAlpha>.01?requestAnimationFrame(e):(ctx.clearRect(0,0,width,height),ctx.globalAlpha=1)}()}window.addEventListener('resize',()=>{width=canvas.width=.8*Math.min(window.innerWidth,window.innerHeight),height=canvas.height=width,centerX=width/2,centerY=height/2}),canvas.addEventListener('mousedown',handleMouseDown),canvas.addEventListener('mousemove',handleMouseMove),canvas.addEventListener('mouseup',handleMouseUp),canvas.addEventListener('mouseleave',handleMouseUp),colorSchemeBtn.addEventListener('click',changeColorScheme),clearBtn.addEventListener('click',clearCanvas),canvas.addEventListener('contextmenu',e=>e.preventDefault()),canvas.addEventListener('dragstart',e=>e.preventDefault()),animate();const instructions=document.createElement('div');instructions.style.cssText='position:fixed;top:20px;color:white;font-size:14px;text-align:center;opacity:0.7;',instructions.textContent='Move your mouse to draw. Use the buttons below to change colors or clear the canvas.',document.body.appendChild(instructions);",
                "language": "javascript"
            },
            {
                "filename": "index.html",
                "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><title>Kaleidoscope Pattern Weaver</title><style>body{margin:0;overflow:hidden;background:#111;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;font-family:Arial,sans-serif}#canvas{border-radius:50%;cursor:crosshair}.controls{position:fixed;bottom:20px;display:flex;gap:10px}.btn{background:rgba(255,255,255,.1);color:#fff;border:1px solid rgba(255,255,255,.2);padding:8px 15px;border-radius:20px;cursor:pointer;transition:all .3s}.btn:hover{background:rgba(255,255,255,.2)}</style></head><body><canvas id="canvas"></canvas><div class="controls"><button id="colorScheme" class="btn">Change Colors</button><button id="clear" class="btn">Clear Canvas</button></div><script src="index.js"></script></body></html>",
                "language": "html"
            }
        ]
    </example_output_4>
    """
    example_5 = """
    <example_input_5>
            Create an interactive soccer field visualization that simulates Portugal's dynamic passing patterns.

            Features:
            - Display a top-down view of a soccer field with standard field markings (lines, center circle, penalty boxes) using HTML canvas.
            - Show 11 red circular nodes representing Portugal's players positioned in a 4-3-3 formation.
            - Each player node should have a small Portuguese flag element above it.
            - Implement an animated passing sequence where a glowing ball travels between player nodes along curved paths.
            - The passing lines should be drawn with a trailing effect in Portugal's national colors (red and green).
            - The ball's movement should have smooth acceleration and deceleration between passes.
            - Display a "Pass Completion Rate" counter at the top of the screen that starts at 100%.
            - Include a speed control slider that adjusts how fast the passing sequence occurs.
            - Implement a user controlled defender that can intercept the ball.
            - When passes fail (when the defender intercepts the ball), the passing and receiving player nodes should briefly flash in a darker shade.
            - The passing sequence should continuously loop, only briefly stopping after an interception.
            - Each player node should slowly oscillate to mimic off the ball movement.

            User Actions:
            1. Use the arrow keys to control the defender. Successfully intercepting the ball will:
            - Cause the current pass to fail
            - Decrease the "Pass Completion Rate" by 5%
            - Create a brief visual disruption effect on the passing line
            2. Use a slider control to adjust the speed of the passing sequence from slow (tactical analysis speed) to fast (match speed).
    </example_input_5>
    <example_output_5>
        [
            {
                "filename": "index.js",
                "content": "const canvas=document.getElementById("field"),ctx=canvas.getContext("2d"),speedSlider=document.getElementById("speedSlider"),completionDisplay=document.getElementById("completion"),width=800,height=600,players=[{x:400,y:500,role:"GK"},{x:200,y:400,role:"LB"},{x:300,y:400,role:"CB"},{x:500,y:400,role:"CB"},{x:600,y:400,role:"RB"},{x:250,y:300,role:"CM"},{x:400,y:250,role:"CM"},{x:550,y:300,role:"CM"},{x:200,y:150,role:"LW"},{x:400,y:100,role:"ST"},{x:600,y:150,role:"RW"}],passingSequence=[[0,2],[2,6],[6,9],[9,8],[8,5],[5,7],[7,10],[10,9],[9,6],[6,3],[3,1]],defender={x:400,y:300,speed:1},keys={ArrowLeft:!1,ArrowRight:!1,ArrowUp:!1,ArrowDown:!1};let passCompletionRate=100,baseSpeed=5,currentPassIndex=0,ballPosition={x:0,y:0},passProgress=0,isPassFailed=!1,oscillationAngle=0;const oscillationSpeed=.02,oscillationRadius=20;canvas.width=width,canvas.height=height,window.addEventListener("keydown",e=>{keys.hasOwnProperty(e.key)&&(keys[e.key]=!0)}),window.addEventListener("keyup",e=>{keys.hasOwnProperty(e.key)&&(keys[e.key]=!1)});function drawField(){ctx.fillStyle="#2e8b57",ctx.fillRect(0,0,width,height),ctx.strokeStyle="#fff",ctx.lineWidth=2,ctx.strokeRect(50,50,width-100,height-100),ctx.beginPath(),ctx.arc(width/2,height/2,60,0,2*Math.PI),ctx.stroke(),ctx.beginPath(),ctx.moveTo(width/2,50),ctx.lineTo(width/2,height-50),ctx.stroke(),drawPenaltyAreas()}function drawPenaltyAreas(){const e=150,t=100;ctx.strokeRect(50,height/2-t/2,e,t),ctx.strokeRect(width-50-e,height/2-t/2,e,t)}function drawPlayers(){oscillationAngle+=oscillationSpeed,players.forEach((e,t)=>{const n=Math.cos(oscillationAngle)*oscillationRadius,r=Math.sin(oscillationAngle)*oscillationRadius;ctx.beginPath(),ctx.arc(e.x+n,e.y+r,15,0,2*Math.PI),ctx.fillStyle=isPassFailed&&(t===passingSequence[currentPassIndex][0]||t===passingSequence[currentPassIndex][1])?"#8b0000":"#ff0000",ctx.fill(),ctx.stroke(),drawFlag(e.x+n,e.y+r-25)}),ctx.beginPath(),ctx.arc(defender.x,defender.y,12,0,2*Math.PI),ctx.fillStyle="#0000FF",ctx.fill(),ctx.stroke()}function drawFlag(e,t){ctx.fillStyle="#006400",ctx.fillRect(e-10,t-5,20,10),ctx.fillStyle="#ff0000",ctx.fillRect(e-10,t-5,8,10)}function drawBall(){const e=players[passingSequence[currentPassIndex][0]],t=players[passingSequence[currentPassIndex][1]],n=passProgress/100,r={x:(e.x+t.x)/2+50,y:(e.y+t.y)/2-50};ballPosition=getBezierPoint(e,r,t,n),ctx.beginPath(),ctx.arc(ballPosition.x,ballPosition.y,8,0,2*Math.PI),ctx.fillStyle="#fff",ctx.fill(),drawPassingLine(e,r,t,n)}function drawPassingLine(e,t,n,r){ctx.beginPath(),ctx.moveTo(e.x,e.y);for(let i=0;i<=r;i+=.1){const r=getBezierPoint(e,t,n,i);ctx.lineTo(r.x,r.y)}ctx.strokeStyle=isPassFailed?"#8b0000":"#006400",ctx.lineWidth=3,ctx.stroke()}function getBezierPoint(e,t,n,r){return{x:Math.pow(1-r,2)*e.x+2*(1-r)*r*t.x+Math.pow(r,2)*n.x,y:Math.pow(1-r,2)*e.y+2*(1-r)*r*t.y+Math.pow(r,2)*n.y}}function update(){const e=baseSpeed*speedSlider.value/5;keys.ArrowLeft&&(defender.x=Math.max(50,defender.x-defender.speed)),keys.ArrowRight&&(defender.x=Math.min(width-50,defender.x+defender.speed)),keys.ArrowUp&&(defender.y=Math.max(50,defender.y-defender.speed)),keys.ArrowDown&&(defender.y=Math.min(height-50,defender.y+defender.speed));const t=Math.hypot(defender.x-ballPosition.x,defender.y-ballPosition.y);t<30&&!isPassFailed&&(isPassFailed=!0,passCompletionRate=Math.max(0,passCompletionRate-5),completionDisplay.textContent=passCompletionRate,setTimeout(()=>{isPassFailed=!1,passProgress=0,currentPassIndex=(currentPassIndex+1)%passingSequence.length},1e3)),isPassFailed||(passProgress+=e,passProgress>=100&&(passProgress=0,currentPassIndex=(currentPassIndex+1)%passingSequence.length))}function animate(){ctx.clearRect(0,0,width,height),drawField(),drawPlayers(),drawBall(),update(),requestAnimationFrame(animate)}animate();",
                "language": "javascript"
            },
            {
                "filename": "index.html",
                "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><title>Portugal Soccer Passing Simulation</title><style>body{margin:0;display:flex;justify-content:center;align-items:center;min-height:100vh;background:#1a1a1a;font-family:Arial,sans-serif}#container{position:relative}#stats{position:absolute;top:10px;left:50%;transform:translateX(-50%);color:#fff;background:rgba(0,0,0,0.7);padding:10px;border-radius:5px;text-align:center}#controls{position:absolute;bottom:10px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,0.7);padding:10px;border-radius:5px;display:flex;gap:20px;align-items:center}#controls label{color:#fff}#speedSlider{width:150px}.btn{background:#006400;color:#fff;border:none;padding:8px 15px;border-radius:5px;cursor:pointer}.btn:hover{background:#008000}</style></head><body><div id="container"><canvas id="field"></canvas><div id="stats">Pass Completion Rate: <span id="completion">100</span>%</div><div id="controls"><label>Speed: <input type="range" id="speedSlider" min="1" max="10" value="5"/></label></div></div><script src="index.js"></script></body></html>",
                "language": "html"
            }
        ]
    </example_output_5>
    """
    examples = [example_1, example_2, example_3, example_4, example_5]
    selection = random.sample(examples, k=2)
    return "".join(selection)


def _get_science_answer_examples() -> str:
    example_1 = """
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
    """
    example_2 = """
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
    example_3 = """
    <example_input_3>
       Create an interactive particle simulation demonstrating the principles of projectile motion and gravitational effects in a military-themed environment.

        Features:
        - Create a side-view scene with a desert landscape background using CSS gradients.
        - Display a launching platform (styled as a military bunker) on the left side of the screen.
        - Implement a targeting system with a visible trajectory arc that updates in real-time as the user adjusts launch parameters.
        - Create particles that follow realistic projectile motion physics, accounting for initial velocity, angle, and gravity.
        - Display real-time data panel showing:
        * Current projectile velocity
        * Launch angle
        * Maximum height reached
        * Wind direction and speed
        - Create three targets on the right side of the screen. When all three targets are hit, they should respawn in new positons.
        - Implement a wind effect and change the wind direction and speed after each launch.
        - Add visual effects for particle launches (small explosion animation at launch).
        - Include particle trail effects that fade over time.
        - Display a score counter for successful target hits.
        - Create a reset button styled as a military command button.

        User Actions:
        1. Use the left/right arrow keys to adjust the launch angle (0-90 degrees). A visual indicator should show the current angle.
        2. Use the up/down arrow keys to adjust the initial launch velocity (shown as a power meter on screen).
        3. Press the spacebar to launch a particle, which will follow the calculated trajectory while being affected by gravity and wind.
    </example_input_3>
    <example_output_3>
        {
            "files": [
                {
                    "filename": "index.js",
                    "content": "document.addEventListener("DOMContentLoaded",()=>{const canvas=document.getElementById("gameCanvas"),ctx=canvas.getContext("2d"),powerFill=document.getElementById("powerFill"),resetBtn=document.getElementById("resetBtn");let canvasSize=Math.min(window.innerWidth,window.innerHeight);canvas.width=canvasSize,canvas.height=canvasSize;const stats={velocity:50,angle:45,maxHeight:0,score:0,wind:0},particles=[],trails=[],targets=[];let isLaunching=!1;class Particle{constructor(x,y,velocity,angle){this.x=x,this.y=y,this.vx=velocity*Math.cos(angle*Math.PI/180),this.vy=-velocity*Math.sin(angle*Math.PI/180),this.trail=[],this.maxHeight=y,this.startTime=Date.now(),this.wind=stats.wind}update(){return this.vy+=.5,this.x+=this.vx+.1*this.wind,this.y+=this.vy,this.y<this.maxHeight&&(this.maxHeight=this.y),this.trail.push({x:this.x,y:this.y,age:0}),this.trail.length>20&&this.trail.shift(),this.trail.forEach(t=>t.age++),this.y<canvas.height}}class Target{constructor(){this.reset()}reset(){this.x=.7*canvas.width+.2*canvas.width*Math.random(),this.y=.7*canvas.height+.2*canvas.height*Math.random(),this.radius=20,this.hit=!1}}function createExplosion(x,y){for(let i=0;i<20;i++){const angle=2*Math.random()*Math.PI,velocity=5*Math.random();trails.push({x:x,y:y,vx:Math.cos(angle)*velocity,vy:Math.sin(angle)*velocity,life:1})}}function updateExplosions(){for(let i=trails.length-1;i>=0;i--){const p=trails[i];p.x+=p.vx,p.y+=p.vy,p.life-=.02,p.life<=0&&trails.splice(i,1)}}function drawBunker(){ctx.fillStyle="#8B7355",ctx.beginPath(),ctx.moveTo(50,canvas.height),ctx.lineTo(50,canvas.height-60),ctx.lineTo(100,canvas.height-60),ctx.lineTo(100,canvas.height),ctx.fill(),ctx.fillStyle="#6B574B",ctx.fillRect(70,canvas.height-80,30,20)}function drawLauncher(){ctx.save(),ctx.translate(85,canvas.height-70),ctx.rotate(-stats.angle*Math.PI/180),ctx.fillStyle="#000000",ctx.fillRect(0,-5,40,10),ctx.restore()}function drawParticles(){particles.forEach(p=>{ctx.fillStyle="#8B0000",ctx.beginPath(),ctx.arc(p.x,p.y,5,0,2*Math.PI),ctx.fill(),ctx.strokeStyle="rgba(139,0,0,0.2)",ctx.beginPath(),p.trail.forEach((point,i)=>{0===i?ctx.moveTo(point.x,point.y):ctx.lineTo(point.x,point.y)}),ctx.stroke()})}function drawExplosions(){trails.forEach(p=>{ctx.fillStyle=`rgba(255,69,0,${p.life})`,ctx.beginPath(),ctx.arc(p.x,p.y,3,0,2*Math.PI),ctx.fill()})}function drawTargets(){targets.forEach(t=>{t.hit||(ctx.fillStyle="#8B0000",ctx.beginPath(),ctx.arc(t.x,t.y,t.radius,0,2*Math.PI),ctx.fill())})}function drawTrajectory(){if(!isLaunching){const points=[],v=stats.velocity,angle=stats.angle,rad=angle*Math.PI/180;let x=85,y=canvas.height-70,vx=v*Math.cos(rad),vy=-v*Math.sin(rad);for(let t=0;t<100;t+=1)if(points.push({x:x,y:y}),vy+=.5,x+=vx+.1*stats.wind,y+=vy,y>canvas.height)break;ctx.strokeStyle="#FF0000",ctx.setLineDash([5,15]),ctx.lineWidth=2,ctx.beginPath(),points.forEach((p,i)=>{0===i?ctx.moveTo(p.x,p.y):ctx.lineTo(p.x,p.y)}),ctx.stroke(),ctx.setLineDash([]),ctx.lineWidth=1}}function updateStats(){document.getElementById("velocity").textContent=stats.velocity.toFixed(1),document.getElementById("angle").textContent=stats.angle.toFixed(1),document.getElementById("maxHeight").textContent=((canvas.height-stats.maxHeight)/10).toFixed(1),document.getElementById("scoreValue").textContent=stats.score}function checkCollisions(){if(particles.forEach(p=>{targets.forEach(t=>{if(!t.hit){const dx=p.x-t.x,dy=p.y-t.y;Math.sqrt(dx*dx+dy*dy)<t.radius&&(t.hit=!0,stats.score++,createExplosion(t.x,t.y))}})}),targets.every(t=>t.hit)){targets.length=0;for(let i=0;i<3;i++)targets.push(new Target)}}function update(){ctx.clearRect(0,0,canvas.width,canvas.height),drawBunker(),drawLauncher(),drawTrajectory(),drawParticles(),drawTargets(),drawExplosions();for(let i=particles.length-1;i>=0;i--)particles[i].update()||particles.splice(i,1);updateExplosions(),checkCollisions(),updateStats(),requestAnimationFrame(update)}function launch(){isLaunching||(isLaunching=!0,particles.push(new Particle(85,canvas.height-70,stats.velocity,stats.angle)),createExplosion(85,canvas.height-70),generateWind(),setTimeout(()=>isLaunching=!1,1e3))}document.addEventListener("keydown",e=>{"ArrowUp"===e.code?(e.preventDefault(),stats.velocity=Math.min(100,stats.velocity+1),powerFill.style.width=`${stats.velocity}%`):"ArrowDown"===e.code?(e.preventDefault(),stats.velocity=Math.max(0,stats.velocity-1),powerFill.style.width=`${stats.velocity}%`):"ArrowLeft"===e.code?(e.preventDefault(),stats.angle=Math.max(0,stats.angle-1)):"ArrowRight"===e.code?(e.preventDefault(),stats.angle=Math.min(90,stats.angle+1)):"Space"===e.code&&(e.preventDefault(),launch())}),resetBtn.addEventListener("click",()=>{particles.length=0,trails.length=0,targets.length=0,stats.score=0;for(let i=0;i<3;i++)targets.push(new Target)});function init(){canvas.width=canvasSize,canvas.height=canvasSize;for(let i=0;i<3;i++)targets.push(new Target);generateWind(),update()}window.addEventListener("resize",()=>{canvasSize=Math.min(window.innerWidth,window.innerHeight),init()});function generateWind(){stats.wind=Math.round(10*(20*Math.random()-10))/10;const windSpeedEl=document.getElementById("windSpeed"),windDirEl=document.getElementById("windDirection");windSpeedEl.textContent=Math.abs(stats.wind),windDirEl.textContent=stats.wind<0?"←":"→"}init()});",
                    "language": "javascript"
                },
                {
                    "filename": "index.html",
                    "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width,initial-scale=1.0" /><title>Military Projectile Simulator</title><style>body,html{margin:0;padding:0;width:100%;height:100%;overflow:hidden;font-family:"Courier New",monospace}#gameCanvas{width:100vmin;height:100vmin;position:relative;background:linear-gradient(180deg,#87ceeb 0%,#87ceeb 60%,#e6b981 65%,#d4a76a 75%,#c19552 85%,#ab824f 100%)}#interface{position:absolute;top:10px;left:10px;background:rgba(35,43,17,0.9);color:#98b06f;padding:15px;border-radius:3px;font-size:14px;border:1px solid #4a5d23;box-shadow:0 0 10px rgba(0,0,0,0.3)}#stats{margin-bottom:10px;text-transform:uppercase;letter-spacing:1px}#powerMeter{width:100px;height:12px;background:#1a1f0e;margin:5px 0;border:1px solid #4a5d23}#powerFill{width:50%;height:100%;background:#98b06f;transition:width 0.3s}#windIndicator{position:absolute;top:10px;right:10px;background:rgba(35,43,17,0.9);color:#98b06f;padding:15px;border-radius:3px;border:1px solid #4a5d23}#score{position:absolute;top:10px;left:50%;transform:translateX(-50%);background:rgba(35,43,17,0.9);color:#98b06f;padding:15px;border-radius:3px;border:1px solid #4a5d23;text-transform:uppercase;letter-spacing:1px}#resetBtn{background:#4a5d23;color:#98b06f;border:1px solid #98b06f;padding:8px 15px;border-radius:3px;cursor:pointer;margin-top:8px;text-transform:uppercase;letter-spacing:1px;font-family:"Courier New",monospace;transition:all 0.3s ease}#resetBtn:hover{background:#98b06f;color:#1a1f0e}#instructions{position:absolute;bottom:10px;left:50%;transform:translateX(-50%);background:rgba(35,43,17,0.9);color:#98b06f;padding:15px;border-radius:3px;font-size:12px;text-align:center;border:1px solid #4a5d23;text-transform:uppercase;letter-spacing:1px}</style></head><body><canvas id="gameCanvas"></canvas><div id="interface"><div id="stats">Velocity: <span id="velocity">50</span> m/s<br />Angle: <span id="angle">45</span>°<br />Max Height: <span id="maxHeight">0</span>m<br />Wind: <span id="windSpeed">0</span> m/s<span id="windDirection">→</span></div><div id="powerMeter"><div id="powerFill"></div></div><button id="resetBtn">RESET</button></div><div id="score">Score: <span id="scoreValue">0</span></div><div id="instructions">↑/↓: Adjust Power | ←/→: Set Angle | Space: Launch</div><script src="index.js"></script></body></html>",
                    "language": "html"
                }
            ]
        }
    </example_output_3>
    """
    example_4 = """
    <example_input_4>
        Create an interactive particle-based jury deliberation simulation that demonstrates the principles of social influence and consensus-building through a physics-based visualization.

        Features:
        - Create a circular deliberation chamber using CSS, styled with a formal courthouse aesthetic (wood textures and neutral colors).
        - Display 12 particle entities representing jurors, each as a circular element with a unique identifier.
        - Each juror particle should have a color gradient representing their current verdict stance (red for guilty, green for not guilty).
        - Implement a physics system where particles can:
        * Move continuously and freely within the chamber bounds
        * Collide elastically with chamber walls and other particles
        * Generate subtle connection lines between nearby particles
        - Create an influence radius around each particle, visualized as a semi-transparent circle.
        - When particles' influence radiuses overlap, their colors should influence each other based on proximity and duration of contact.
        - Display a real-time statistics panel showing:
        * Current distribution of verdicts
        * Time elapsed in deliberation
        * Number of significant interactions (when particles stay in proximity for over 3 seconds)
        - Add visual effects for particle interactions (subtle glow when particles influence each other).
        - Create a reset button styled as a formal gavel icon.

        User Actions:
        1. Click and drag individual particles to manually position them, simulating directed jury interactions.
        2. Right-click any particle to temporarily "lock" its opinion, preventing it from being influenced by others (simulating a strongly convinced juror).
    </example_input_4>
    <example_output_4>
     {
        "files": [
            {
                "filename": "index.js",
                "content": "document.addEventListener("DOMContentLoaded",()=>{const chamber=document.getElementById("chamber");const canvas=document.createElement("canvas");const ctx=canvas.getContext("2d");chamber.appendChild(canvas);let width=chamber.clientWidth;let height=chamber.clientHeight;canvas.width=width;canvas.height=height;const particles=[];let draggedParticle=null;let interactionCount=0;let startTime=Date.now();class Particle{constructor(x,y,id){this.x=x;this.y=y;this.id=id;this.vx=(Math.random()-0.5)*4;this.vy=(Math.random()-0.5)*4;this.radius=15;this.influenceRadius=60;this.opinion=Math.random();this.locked=false;this.lastInteractionTime={};this.brownianIntensity=0.2}update(){this.vx+=(Math.random()-0.5)*this.brownianIntensity;this.vy+=(Math.random()-0.5)*this.brownianIntensity;this.vx*=0.995;this.vy*=0.995;this.x+=this.vx;this.y+=this.vy;if(this.x-this.radius<0){this.x=this.radius;this.vx=Math.abs(this.vx)*0.9}else if(this.x+this.radius>width){this.x=width-this.radius;this.vx=-Math.abs(this.vx)*0.9}if(this.y-this.radius<0){this.y=this.radius;this.vy=Math.abs(this.vy)*0.9}else if(this.y+this.radius>height){this.y=height-this.radius;this.vy=-Math.abs(this.vy)*0.9}const centerX=width/2;const centerY=height/2;const distToCenter=Math.sqrt((this.x-centerX)**2+(this.y-centerY)**2);const maxDist=Math.min(width,height)/2-this.radius;if(distToCenter>maxDist){const angle=Math.atan2(this.y-centerY,this.x-centerX);this.x=centerX+Math.cos(angle)*maxDist;this.y=centerY+Math.sin(angle)*maxDist;this.vx*=0.9;this.vy*=0.9}}draw(){ctx.beginPath();const gradient=ctx.createRadialGradient(this.x,this.y,0,this.x,this.y,this.radius);const color=this.getColor();gradient.addColorStop(0,color);gradient.addColorStop(1,this.locked?"rgba(128,128,128,0.8)":color.replace("1)","0.8)"));ctx.fillStyle=gradient;ctx.arc(this.x,this.y,this.radius,0,Math.PI*2);ctx.fill();ctx.strokeStyle="rgba(255,255,255,0.3)";ctx.stroke();ctx.fillStyle="white";ctx.font="10px Georgia";ctx.textAlign="center";ctx.textBaseline="middle";ctx.fillText(this.id,this.x,this.y);ctx.beginPath();ctx.arc(this.x,this.y,this.influenceRadius,0,Math.PI*2);ctx.strokeStyle=`rgba(255,255,255,${this.locked?0.1:0.2})`;ctx.stroke()}getColor(){return this.opinion<0.5?"rgba(255,50,50,1)":"rgba(50,255,50,1)"}interact(other){if(this.locked&&other.locked)return;const dx=other.x-this.x;const dy=other.y-this.y;const distance=Math.sqrt(dx*dx+dy*dy);if(distance<this.influenceRadius){const now=Date.now();const key=Math.min(this.id,other.id)+"-"+Math.max(this.id,other.id);if(!this.lastInteractionTime[key]){this.lastInteractionTime[key]=now}if(now-this.lastInteractionTime[key]>3000){interactionCount++;this.lastInteractionTime[key]=now}const influence=0.01*(1-distance/this.influenceRadius);if(!this.locked){this.opinion+=(other.opinion-this.opinion)*influence}ctx.beginPath();ctx.moveTo(this.x,this.y);ctx.lineTo(other.x,other.y);ctx.strokeStyle=`rgba(255,255,255,${0.1*(1-distance/this.influenceRadius)})`;ctx.stroke()}}}function init(){particles.length=0;for(let i=0;i<12;i++){const angle=i*((Math.PI*2)/12);const r=Math.min(width,height)/4;const x=width/2+r*Math.cos(angle);const y=height/2+r*Math.sin(angle);particles.push(new Particle(x,y,i+1))}interactionCount=0;startTime=Date.now()}function updateStats(){const counts={guilty:0,notGuilty:0};particles.forEach(p=>{if(p.opinion<0.5)counts.guilty++;else counts.notGuilty++});document.getElementById("guilty").textContent=counts.guilty;document.getElementById("notGuilty").textContent=counts.notGuilty;const elapsed=Math.floor((Date.now()-startTime)/1000);const minutes=Math.floor(elapsed/60).toString().padStart(2,"0");const seconds=(elapsed%60).toString().padStart(2,"0");document.getElementById("time").textContent=`${minutes}:${seconds}`;document.getElementById("interactions").textContent=interactionCount}function animate(){ctx.clearRect(0,0,width,height);particles.forEach(p1=>{particles.forEach(p2=>{if(p1!==p2)p1.interact(p2)})});particles.forEach(p=>p.update());particles.forEach(p=>p.draw());updateStats();requestAnimationFrame(animate)}canvas.addEventListener("mousedown",e=>{const rect=canvas.getBoundingClientRect();const x=e.clientX-rect.left;const y=e.clientY-rect.top;particles.forEach(p=>{const dx=p.x-x;const dy=p.y-y;if(Math.sqrt(dx*dx+dy*dy)<p.radius){draggedParticle=p}})});canvas.addEventListener("mousemove",e=>{if(draggedParticle){const rect=canvas.getBoundingClientRect();draggedParticle.x=e.clientX-rect.left;draggedParticle.y=e.clientY-rect.top}});canvas.addEventListener("mouseup",()=>{draggedParticle=null});canvas.addEventListener("contextmenu",e=>{e.preventDefault();const rect=canvas.getBoundingClientRect();const x=e.clientX-rect.left;const y=e.clientY-rect.top;particles.forEach(p=>{const dx=p.x-x;const dy=p.y-y;if(Math.sqrt(dx*dx+dy*dy)<p.radius){p.locked=!p.locked}})});document.getElementById("reset").addEventListener("click",init);window.addEventListener("resize",()=>{width=chamber.clientWidth;height=chamber.clientHeight;canvas.width=width;canvas.height=height});init();animate()});",
                "language": "javascript"

            },
            {
                "filename": "index.html",
                "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><title>Jury Deliberation Simulation</title><style>body,html{margin:0;padding:0;width:100%;height:100%;overflow:hidden;font-family:Georgia,serif;background:#2b2b2b}#container{width:100vmin;height:100vmin;position:relative;margin:auto;display:flex;justify-content:center;align-items:center}#chamber{width:80%;height:80%;border-radius:50%;background:linear-gradient(45deg,#8b7355,#a0522d);box-shadow:inset 0 0 50px rgba(0,0,0,0.5),0 0 20px rgba(0,0,0,0.3);position:relative;border:15px solid #654321}#stats{position:absolute;top:10px;right:10px;background:rgba(51,33,29,0.9);color:#d4c4b7;padding:15px;border-radius:5px;font-size:14px;border:1px solid #654321}#reset{position:absolute;top:10px;left:10px;background:#654321;border:none;color:#d4c4b7;padding:10px;border-radius:5px;cursor:pointer;display:flex;align-items:center;gap:5px;font-family:Georgia,serif}#reset:hover{background:#8b7355}#instructions{position:absolute;bottom:10px;left:50%;transform:translateX(-50%);background:rgba(51,33,29,0.9);color:#d4c4b7;padding:10px;border-radius:5px;font-size:12px;text-align:center;width:80%;max-width:500px}.gavel{width:20px;height:20px;background:#d4c4b7;clip-path:polygon(0 20%,100% 20%,100% 40%,0 40%,0 60%,100% 60%,100% 80%,0 80%)}</style></head><body><div id="container"><div id="chamber"></div><div id="stats">Verdict Distribution:<br />Guilty: <span id="guilty">0</span><br />Not Guilty: <span id="notGuilty">0</span><br /><br />Time: <span id="time">00:00</span><br />Interactions: <span id="interactions">0</span></div><button id="reset"><div class="gavel"></div>Reset</button><div id="instructions">Click and drag jurors to position them<br />Right-click: Lock/unlock juror opinion</div></div><script src="index.js"></script></body></html>",
                "language": "html"
            }
        ]
     }
    </example_output_4>
    """
    example_5 = """
    <example_input_5>
        Create an interactive orbital mechanics simulation that demonstrates Kepler's Laws of Planetary Motion through a simplified 2D visualization of a solar system.

        Features:
        - Create a dark space background with a subtle star field effect using CSS.
        - Display a central star (sun) in the center of the screen using gradients to create a glowing effect.
        - Create a movable planet that orbits the central star following Kepler's First Law (elliptical orbit).
        - Implement simplified gravitational physics where:
        * The planet's velocity changes based on its distance from the star (demonstrating Kepler's Second Law)
        * The orbit's period is mathematically related to its semi-major axis (demonstrating Kepler's Third Law)
        - Display a faint elliptical orbit line that updates in real-time as orbital parameters change.
        - Show a real-time data panel styled as a telescope display interface, containing:
        * Current orbital period
        * Current velocity
        * Distance from star
        * Orbital eccentricity
        - Create orbital trail effects that fade over time, showing the planet's recent path.
        - Add visual effects for the planet (subtle glow based on its proximity to the star).
        - Implement a "telescopic view" aesthetic with circular vignette corners and grid lines.
        - Include a reset button styled as a telescope adjustment knob.

        User Actions:
        1. Click and drag anywhere on the orbital path to adjust its shape and size. The ellipse should deform smoothly following the mouse, while maintaining the star at one focus (demonstrating Kepler's First Law). The planet's motion should automatically adjust to the new orbital parameters.
        2. Press and hold the spacebar to enter "time warp" mode, increasing the simulation speed to better observe long-term orbital behavior. Release to return to normal speed.    </example_input_5>
    <example_output_5>
        {
            "files": [
                {
                    "filename": "index.js",
                    "content": "document.addEventListener("DOMContentLoaded",()=>{const canvas=document.getElementById("gameCanvas"),ctx=canvas.getContext("2d"),resetBtn=document.getElementById("resetBtn");let canvasSize=Math.min(window.innerWidth,window.innerHeight);canvas.width=canvasSize;canvas.height=canvasSize;const center={x:canvas.width/2,y:canvas.height/2},state={timeScale:1,isDragging:!1,dragPoint:{x:0,y:0}},orbit={a:canvas.width/4,b:canvas.width/5,angle:0,period:2*Math.PI,timeElapsed:0,trail:[]};function createStars(e=200){const t=[];for(let n=0;n<e;n++)t.push({x:Math.random()*canvas.width,y:Math.random()*canvas.height,brightness:Math.random()});return t}const stars=createStars();function drawStar(){const e=ctx.createRadialGradient(center.x,center.y,0,center.x,center.y,50);e.addColorStop(0,"#fff"),e.addColorStop(.2,"#ffdc78"),e.addColorStop(.4,"#ff9340"),e.addColorStop(1,"rgba(255,69,0,0)"),ctx.beginPath(),ctx.fillStyle=e,ctx.arc(center.x,center.y,50,0,2*Math.PI),ctx.fill()}function drawStars(){ctx.fillStyle="#fff",stars.forEach(e=>{ctx.globalAlpha=.5*e.brightness,ctx.beginPath(),ctx.arc(e.x,e.y,1,0,2*Math.PI),ctx.fill()}),ctx.globalAlpha=1}function calculateOrbitPoint(e){const t=e%(2*Math.PI),n=orbit.a*(1-.4)/(1+.4*Math.cos(t));return{x:center.x+n*Math.cos(t),y:center.y+n*Math.sin(t)}}function drawOrbit(){ctx.strokeStyle="rgba(74,158,255,0.3)",ctx.beginPath();for(let e=0;e<2*Math.PI;e+=.1){const t=calculateOrbitPoint(e);0===e?ctx.moveTo(t.x,t.y):ctx.lineTo(t.x,t.y)}ctx.closePath(),ctx.stroke()}function drawPlanet(e){const t=Math.sqrt(Math.pow(e.x-center.x,2)+Math.pow(e.y-center.y,2)),n=Math.max(10,20-t/100),a=ctx.createRadialGradient(e.x,e.y,0,e.x,e.y,n);a.addColorStop(0,"#4a9eff"),a.addColorStop(1,"rgba(74,158,255,0)"),ctx.beginPath(),ctx.fillStyle=a,ctx.arc(e.x,e.y,n,0,2*Math.PI),ctx.fill(),ctx.beginPath(),ctx.fillStyle="#2d5a8c",ctx.arc(e.x,e.y,8,0,2*Math.PI),ctx.fill()}function drawTrail(){ctx.strokeStyle="rgba(74,158,255,0.2)",ctx.beginPath(),orbit.trail.forEach((e,t)=>{0===t?ctx.moveTo(e.x,e.y):ctx.lineTo(e.x,e.y)}),ctx.stroke()}function updateStats(e){const t=Math.sqrt(Math.pow(e.x-center.x,2)+Math.pow(e.y-center.y,2)),n=2e3*Math.sqrt(1/t);document.getElementById("period").textContent=(orbit.period/Math.PI).toFixed(1),document.getElementById("velocity").textContent=n.toFixed(1),document.getElementById("distance").textContent=(t/100).toFixed(2),document.getElementById("eccentricity").textContent="0.4"}function update(e){ctx.clearRect(0,0,canvas.width,canvas.height),drawStars(),drawStar(),drawOrbit();const t=calculateOrbitPoint(orbit.timeElapsed);orbit.trail.push({...t}),orbit.trail.length>50&&orbit.trail.shift(),drawTrail(),drawPlanet(t),updateStats(t),state.timeScale>1?orbit.timeElapsed+=.02*state.timeScale:orbit.timeElapsed+=.02,requestAnimationFrame(update)}function handleDrag(e){if(state.isDragging){const t=canvas.getBoundingClientRect(),n=(e.clientX-t.left)*(canvas.width/t.width),a=(e.clientY-t.top)*(canvas.height/t.height),r=n-center.x,i=a-center.y;orbit.a=Math.sqrt(r*r+i*i),orbit.b=.8*orbit.a,orbit.period=2*Math.PI*Math.sqrt(Math.pow(orbit.a,3))}}canvas.addEventListener("mousedown",e=>{state.isDragging=!0}),canvas.addEventListener("mousemove",handleDrag),canvas.addEventListener("mouseup",()=>{state.isDragging=!1}),document.addEventListener("keydown",e=>{"Space"===e.code&&(e.preventDefault(),state.timeScale=5)}),document.addEventListener("keyup",e=>{"Space"===e.code&&(state.timeScale=1)}),resetBtn.addEventListener("click",()=>{orbit.a=canvas.width/4,orbit.b=canvas.width/5,orbit.timeElapsed=0,orbit.trail=[]}),window.addEventListener("resize",()=>{canvasSize=Math.min(window.innerWidth,window.innerHeight),canvas.width=canvasSize,canvas.height=canvasSize,center.x=canvas.width/2,center.y=canvas.height/2}),update()});",
                    "language": "javascript"
                },
                {
                    "filename": "index.html",
                    "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width,initial-scale=1.0" /><title>Orbital Mechanics Simulator</title><style>body,html{margin:0;padding:0;width:100%;height:100%;overflow:hidden;font-family:"Courier New",monospace;background:#000}#gameCanvas{width:100vmin;height:100vmin;position:relative;background:radial-gradient(circle at center,#000 0%,#090618 100%)}#interface{position:absolute;top:10px;left:10px;background:rgba(16,24,48,0.85);color:#4a9eff;padding:15px;border-radius:50px;font-size:14px;border:1px solid #234;box-shadow:0 0 20px rgba(74,158,255,0.2)}#stats{margin-bottom:10px;text-transform:uppercase;letter-spacing:1px}#resetBtn{background:#234;color:#4a9eff;border:2px solid #4a9eff;padding:8px 15px;border-radius:50%;cursor:pointer;margin-top:8px;width:50px;height:50px;display:flex;align-items:center;justify-content:center;transition:all 0.3s ease}#resetBtn:hover{background:#4a9eff;color:#000}#instructions{position:absolute;bottom:10px;left:50%;transform:translateX(-50%);background:rgba(16,24,48,0.85);color:#4a9eff;padding:15px;border-radius:25px;font-size:12px;text-align:center;border:1px solid #234}#container{width:100vmin;height:100vmin;position:relative;margin:auto;overflow:hidden}.vignette{position:absolute;top:0;left:0;width:100%;height:100%;box-shadow:inset 0 0 150px rgba(0,0,0,0.9);pointer-events:none;border-radius:50%}.grid{position:absolute;top:0;left:0;width:100%;height:100%;background-image:linear-gradient(rgba(74,158,255,0.1) 1px,transparent 1px),linear-gradient(90deg,rgba(74,158,255,0.1) 1px,transparent 1px);background-size:50px 50px;pointer-events:none}</style></head><body><div id="container"><canvas id="gameCanvas"></canvas><div class="vignette"></div><div class="grid"></div><div id="interface"><div id="stats">Period: <span id="period">0.0</span>s<br />Velocity: <span id="velocity">0.0</span>km/s<br />Distance: <span id="distance">0.0</span>AU<br />Eccentricity: <span id="eccentricity">0.0</span></div><button id="resetBtn">RESET</button></div><div id="instructions">Click & Drag Orbit to Adjust | Hold Space for Time Warp</div></div><script src="index.js"></script></body></html>",
                    "language": "html"
                }
            ]
        }
    </example_output_5>
    """

    examples = [example_1, example_2, example_3, example_4, example_5]
    selection = random.sample(examples, k=2)
    return "".join(selection)
