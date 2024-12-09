import subprocess

from pydantic import BaseModel, Field


class LintResult(BaseModel):
    return_code: int = Field(description="status code returned from ESLint")
    output: str = Field(description="stdout messages from ESLint")
    error: str = Field(description="stderr messages from ESLint")
    input: str = Field(description="input code passed to ESLint")


def setup_linting():
    """Set up the linting environment by ensuring ESLint is installed."""
    try:
        # Check if npm is available
        subprocess.run(["npm", "--version"], capture_output=True, check=True)

        # Install ESLint locally if not present
        subprocess.run(["npm", "install", "eslint"], capture_output=True, check=True)
        return True
    except subprocess.SubprocessError as e:
        print(f"Failed to set up linting environment: {e}")
        return False


def lint_code(code: str) -> LintResult:
    try:
        # Check if eslint is installed
        npm_check = subprocess.run(
            ["npm", "list", "eslint"],
            capture_output=True,
            text=True,
            check=False,
        )
        if npm_check.returncode != 0:
            setup_linting()
        result = subprocess.run(
            [
                "npx",
                "eslint",
                "--quiet",  # only report errors, ignore warnings
                "--stdin",  # read from stdin instead of default behaviour of files
            ],
            input=code,
            capture_output=True,
            text=True,
            check=False,
        )

        return LintResult(
            return_code=result.returncode,
            output=result.stdout,
            error=result.stderr,
            input=code,
        )
    except Exception as e:
        print(f"Subprocess error: {str(e)}")
        return LintResult(
            return_code=0,
            output="",
            error=str(e),
            input=code,
        )


def main():
    print(setup_linting())

    bad_code = """
        const GAME_DURATION = 120;  // 2 minutes
        const MAX_WORKERS = 8;
        const WORK_ZONES = ['collaborative', 'quiet', 'brainstorming'];

        class GameWorker {
            constructor(id) {
                this.id = id;
                this.motivation = 50 + Math.random() * 50;
                this.energy = 100;
                this.mood = this.getMoodState();
                this.workStyle = WORK_ZONES[Math.floor(Math.random() * WORK_ZONES.length)];
                this.element = this.createWorkerElement();
            }

            createWorkerElement() {
                const worker = document.createElement('div');
                worker.className = 'worker';
                worker.innerHTML = `
                    <div class="worker-mood" style="background-color: ${this.getMoodColor()}"></div>
                    <div class="worker-energy" style="width: ${this.energy}%"></div>
                    <div class="worker-motivation" style="width: ${this.motivation}%"></div>
                `;
                worker.addEventListener('click', () => this.boostMotivation());
                return worker;
            }

            getMoodState() {
                if (this.motivation > 75) return 'happy';
                if (this.motivation > 25) return 'neutral';
                return 'stressed';
            }

            getMoodColor() {
                const moodColors = {
                    'happy': '#2ecc71',
                    'neutral': '#f39c12',
                    'stressed': '#e74c3c'
                };
                return moodColors[this.getMoodState()];
            }

            boostMotivation() {
                this.motivation = Math.min(100, this.motivation + 20);
                this.energy = Math.min(100, this.energy + 15);
                this.updateVisuals();
            }

            updateVisuals() {
                const moodElement = this.element.querySelector('.worker-mood');
                const energyElement = this.element.querySelector('.worker-energy');
                const motivationElement = this.element.querySelector('.worker-motivation');

                moodElement.style.backgroundColor = this.getMoodColor();
                energyElement.style.width = `${this.energy}%`;
                motivationElement.style.width = `${this.motivation}%`;
            }
        }

        class MotivationMayhem {
            constructor() {
                this.workers = [];
                this.productivityScore = 0;
                this.timeLeft = GAME_DURATION;
                this.achievements = [];
                this.initGame();
            }

            initGame() {
                this.createWorkers();
                this.startTimer();
                this.generateRandomEvents();
            }

            createWorkers() {
                const workersContainer = document.getElementById('workers');
                for (let i = 0; i < MAX_WORKERS; i++) {
                    const worker = new GameWorker(i);
                    this.workers.push(worker);
                    workersContainer.appendChild(worker.element);
                }
            }

            startTimer() {
                const timerElement = document.getElementById('timer');
                const gameInterval = setInterval(() => {
                    this.timeLeft--;
                    timerElement.textContent = this.timeLeft;
                    this.updateProductivity();

                    if (this.timeLeft <= 0) {
                        clearInterval(gameInterval);
                        this.endGame();
                    }
                }, 1000);
            }

            updateProductivity() {
                const averageMotivation = this.workers.reduce((sum, worker) => sum + worker.motivation, 0) / this.workers.length;
                this.productivityScore = Math.floor(averageMotivation);
                document.getElementById('productivityScore').textContent = this.productivityScore;
                this.checkAchievements();
            }

            generateRandomEvents() {
                setInterval(() => {
                    const randomEvent = Math.random();
                    if (randomEvent < 0.3) this.coffeeBreakerEvent();
                    if (randomEvent > 0.7) this.teamConflictEvent();
                }, 10000);
            }

            coffeeBreakerEvent() {
                this.workers.forEach(worker => {
                    worker.motivation = Math.min(100, worker.motivation + 15);
                    worker.updateVisuals();
                });
            }

            teamConflictEvent() {
                this.workers.forEach(worker => {
                    worker.motivation = Math.max(0, worker.motivation - 10);
                    worker.updateVisuals();
                });
            }

            checkAchievements() {
                const highMotivationAchievement = this.workers.every(worker => worker.motivation > 90);
                const lowConflictAchievement = this.productivityScore > 80;

                if (highMotivationAchievement && !this.achievements.includes('high_motivation')) {
                    this.achievements.push('high_motivation');
                    this.displayAchievement('High Team Motivation');
                }

                if (lowConflictAchievement && !this.achievements.includes('low_conflict')) {
                    this.achievements.push('low_conflict');
                    this.displayAchievement('Low Workplace Conflict');
                }
            }

            displayAchievement(text) {
                const achievementsContainer = document.getElementById('achievements');
                const badge = document.createElement('div');
                badge.title = text;
                achievementsContainer.appendChild(badge);
            }

            endGame() {
                document.getElementById('gameOver').style.display = 'block';
                document.getElementById('finalScore').textContent = this.productivityScore;
            }
        }

        function restartGame() {
            document.getElementById('gameOver').style.display = 'none';
            document.getElementById('workers').innerHTML = '';
            document.getElementById('achievements').innerHTML = '';
            new MotivationMayhem();
        }

        // Start the game
        new MotivationMayhem();
    """
    # good_code = """
    # const fuck = ["citizen", "resident", "smile's", "undocumented"]
    # console.log(fuck)
    # """
    # print(lint_code(bad_code))
    lint_code(bad_code)


if __name__ == "__main__":
    main()

"""
- eslint only catches first error in file, so might need to loop the results back thru the linter 
"""
