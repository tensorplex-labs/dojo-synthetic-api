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
    examples = [example_1, example_2, example_3]
    selection = random.choices(examples, k=2)
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
    example_1 = """
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
    examples = [example_1, example_2]
    return random.choice(examples)


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
    [
        {
            "filename": "index.html",
            "content": "<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width,initial-scale=1.0" /><title>Military Projectile Simulator</title><style>body,html{margin:0;padding:0;width:100%;height:100%;overflow:hidden;font-family:"Courier New",monospace}#gameCanvas{width:100vmin;height:100vmin;position:relative;background:linear-gradient(180deg,#87ceeb 0%,#87ceeb 60%,#e6b981 65%,#d4a76a 75%,#c19552 85%,#ab824f 100%)}#interface{position:absolute;top:10px;left:10px;background:rgba(35,43,17,0.9);color:#98b06f;padding:15px;border-radius:3px;font-size:14px;border:1px solid #4a5d23;box-shadow:0 0 10px rgba(0,0,0,0.3)}#stats{margin-bottom:10px;text-transform:uppercase;letter-spacing:1px}#powerMeter{width:100px;height:12px;background:#1a1f0e;margin:5px 0;border:1px solid #4a5d23}#powerFill{width:50%;height:100%;background:#98b06f;transition:width 0.3s}#windIndicator{position:absolute;top:10px;right:10px;background:rgba(35,43,17,0.9);color:#98b06f;padding:15px;border-radius:3px;border:1px solid #4a5d23}#score{position:absolute;top:10px;left:50%;transform:translateX(-50%);background:rgba(35,43,17,0.9);color:#98b06f;padding:15px;border-radius:3px;border:1px solid #4a5d23;text-transform:uppercase;letter-spacing:1px}#resetBtn{background:#4a5d23;color:#98b06f;border:1px solid #98b06f;padding:8px 15px;border-radius:3px;cursor:pointer;margin-top:8px;text-transform:uppercase;letter-spacing:1px;font-family:"Courier New",monospace;transition:all 0.3s ease}#resetBtn:hover{background:#98b06f;color:#1a1f0e}#instructions{position:absolute;bottom:10px;left:50%;transform:translateX(-50%);background:rgba(35,43,17,0.9);color:#98b06f;padding:15px;border-radius:3px;font-size:12px;text-align:center;border:1px solid #4a5d23;text-transform:uppercase;letter-spacing:1px}</style></head><body><canvas id="gameCanvas"></canvas><div id="interface"><div id="stats">Velocity: <span id="velocity">50</span> m/s<br />Angle: <span id="angle">45</span>°<br />Max Height: <span id="maxHeight">0</span>m<br />Wind: <span id="windSpeed">0</span> m/s<span id="windDirection">→</span></div><div id="powerMeter"><div id="powerFill"></div></div><button id="resetBtn">RESET</button></div><div id="score">Score: <span id="scoreValue">0</span></div><div id="instructions">↑/↓: Adjust Power | ←/→: Set Angle | Space: Launch</div><script src="index.js"></script></body></html>",
            "language": "html"
        },
        {
            "filename": "index.js",
            "content": "document.addEventListener("DOMContentLoaded",()=>{const canvas=document.getElementById("gameCanvas"),ctx=canvas.getContext("2d"),powerFill=document.getElementById("powerFill"),resetBtn=document.getElementById("resetBtn");let canvasSize=Math.min(window.innerWidth,window.innerHeight);canvas.width=canvasSize,canvas.height=canvasSize;const stats={velocity:50,angle:45,maxHeight:0,score:0,wind:0},particles=[],trails=[],targets=[];let isLaunching=!1;class Particle{constructor(x,y,velocity,angle){this.x=x,this.y=y,this.vx=velocity*Math.cos(angle*Math.PI/180),this.vy=-velocity*Math.sin(angle*Math.PI/180),this.trail=[],this.maxHeight=y,this.startTime=Date.now(),this.wind=stats.wind}update(){return this.vy+=.5,this.x+=this.vx+.1*this.wind,this.y+=this.vy,this.y<this.maxHeight&&(this.maxHeight=this.y),this.trail.push({x:this.x,y:this.y,age:0}),this.trail.length>20&&this.trail.shift(),this.trail.forEach(t=>t.age++),this.y<canvas.height}}class Target{constructor(){this.reset()}reset(){this.x=.7*canvas.width+.2*canvas.width*Math.random(),this.y=.7*canvas.height+.2*canvas.height*Math.random(),this.radius=20,this.hit=!1}}function createExplosion(x,y){for(let i=0;i<20;i++){const angle=2*Math.random()*Math.PI,velocity=5*Math.random();trails.push({x:x,y:y,vx:Math.cos(angle)*velocity,vy:Math.sin(angle)*velocity,life:1})}}function updateExplosions(){for(let i=trails.length-1;i>=0;i--){const p=trails[i];p.x+=p.vx,p.y+=p.vy,p.life-=.02,p.life<=0&&trails.splice(i,1)}}function drawBunker(){ctx.fillStyle="#8B7355",ctx.beginPath(),ctx.moveTo(50,canvas.height),ctx.lineTo(50,canvas.height-60),ctx.lineTo(100,canvas.height-60),ctx.lineTo(100,canvas.height),ctx.fill(),ctx.fillStyle="#6B574B",ctx.fillRect(70,canvas.height-80,30,20)}function drawLauncher(){ctx.save(),ctx.translate(85,canvas.height-70),ctx.rotate(-stats.angle*Math.PI/180),ctx.fillStyle="#000000",ctx.fillRect(0,-5,40,10),ctx.restore()}function drawParticles(){particles.forEach(p=>{ctx.fillStyle="#8B0000",ctx.beginPath(),ctx.arc(p.x,p.y,5,0,2*Math.PI),ctx.fill(),ctx.strokeStyle="rgba(139,0,0,0.2)",ctx.beginPath(),p.trail.forEach((point,i)=>{0===i?ctx.moveTo(point.x,point.y):ctx.lineTo(point.x,point.y)}),ctx.stroke()})}function drawExplosions(){trails.forEach(p=>{ctx.fillStyle=`rgba(255,69,0,${p.life})`,ctx.beginPath(),ctx.arc(p.x,p.y,3,0,2*Math.PI),ctx.fill()})}function drawTargets(){targets.forEach(t=>{t.hit||(ctx.fillStyle="#8B0000",ctx.beginPath(),ctx.arc(t.x,t.y,t.radius,0,2*Math.PI),ctx.fill())})}function drawTrajectory(){if(!isLaunching){const points=[],v=stats.velocity,angle=stats.angle,rad=angle*Math.PI/180;let x=85,y=canvas.height-70,vx=v*Math.cos(rad),vy=-v*Math.sin(rad);for(let t=0;t<100;t+=1)if(points.push({x:x,y:y}),vy+=.5,x+=vx+.1*stats.wind,y+=vy,y>canvas.height)break;ctx.strokeStyle="#FF0000",ctx.setLineDash([5,15]),ctx.lineWidth=2,ctx.beginPath(),points.forEach((p,i)=>{0===i?ctx.moveTo(p.x,p.y):ctx.lineTo(p.x,p.y)}),ctx.stroke(),ctx.setLineDash([]),ctx.lineWidth=1}}function updateStats(){document.getElementById("velocity").textContent=stats.velocity.toFixed(1),document.getElementById("angle").textContent=stats.angle.toFixed(1),document.getElementById("maxHeight").textContent=((canvas.height-stats.maxHeight)/10).toFixed(1),document.getElementById("scoreValue").textContent=stats.score}function checkCollisions(){if(particles.forEach(p=>{targets.forEach(t=>{if(!t.hit){const dx=p.x-t.x,dy=p.y-t.y;Math.sqrt(dx*dx+dy*dy)<t.radius&&(t.hit=!0,stats.score++,createExplosion(t.x,t.y))}})}),targets.every(t=>t.hit)){targets.length=0;for(let i=0;i<3;i++)targets.push(new Target)}}function update(){ctx.clearRect(0,0,canvas.width,canvas.height),drawBunker(),drawLauncher(),drawTrajectory(),drawParticles(),drawTargets(),drawExplosions();for(let i=particles.length-1;i>=0;i--)particles[i].update()||particles.splice(i,1);updateExplosions(),checkCollisions(),updateStats(),requestAnimationFrame(update)}function launch(){isLaunching||(isLaunching=!0,particles.push(new Particle(85,canvas.height-70,stats.velocity,stats.angle)),createExplosion(85,canvas.height-70),generateWind(),setTimeout(()=>isLaunching=!1,1e3))}document.addEventListener("keydown",e=>{"ArrowUp"===e.code?(e.preventDefault(),stats.velocity=Math.min(100,stats.velocity+1),powerFill.style.width=`${stats.velocity}%`):"ArrowDown"===e.code?(e.preventDefault(),stats.velocity=Math.max(0,stats.velocity-1),powerFill.style.width=`${stats.velocity}%`):"ArrowLeft"===e.code?(e.preventDefault(),stats.angle=Math.max(0,stats.angle-1)):"ArrowRight"===e.code?(e.preventDefault(),stats.angle=Math.min(90,stats.angle+1)):"Space"===e.code&&(e.preventDefault(),launch())}),resetBtn.addEventListener("click",()=>{particles.length=0,trails.length=0,targets.length=0,stats.score=0;for(let i=0;i<3;i++)targets.push(new Target)});function init(){canvas.width=canvasSize,canvas.height=canvasSize;for(let i=0;i<3;i++)targets.push(new Target);generateWind(),update()}window.addEventListener("resize",()=>{canvasSize=Math.min(window.innerWidth,window.innerHeight),init()});function generateWind(){stats.wind=Math.round(10*(20*Math.random()-10))/10;const windSpeedEl=document.getElementById("windSpeed"),windDirEl=document.getElementById("windDirection");windSpeedEl.textContent=Math.abs(stats.wind),windDirEl.textContent=stats.wind<0?"←":"→"}init()});",
            "language": "javascript"
        }
    ]
    </example_output_3>
    """
    examples = [example_1, example_2, example_3]
    selection = random.choices(examples, k=2)
    return "".join(selection)
