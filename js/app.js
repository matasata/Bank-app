/**
 * 1st Edition AD&D Character Generator - Main Application
 */

const App = {
    state: {
        currentStep: 0,
        method: null,
        methodResult: null,
        abilities: null,
        adjustedAbilities: null,
        race: null,
        className: null,
        alignment: null,
        character: null
    },

    steps: ['step-method', 'step-abilities', 'step-race', 'step-class', 'step-alignment', 'step-finalize', 'step-sheet'],

    init() {
        this.setupMethodCards();
        this.setupNavigation();
        this.setupStepIndicators();
        this.goToStep(0);
    },

    setupMethodCards() {
        document.querySelectorAll('.method-card').forEach(card => {
            card.addEventListener('click', () => {
                document.querySelectorAll('.method-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                this.state.method = parseInt(card.dataset.method);
                document.getElementById('btn-next').disabled = false;
            });
        });
    },

    setupNavigation() {
        document.getElementById('btn-next').addEventListener('click', () => this.nextStep());
        document.getElementById('btn-back').addEventListener('click', () => this.prevStep());
        document.getElementById('btn-new').addEventListener('click', () => this.reset());
        document.getElementById('btn-print').addEventListener('click', () => window.print());
    },

    setupStepIndicators() {
        const indicators = document.getElementById('step-indicators');
        const labels = ['Method', 'Abilities', 'Race', 'Class', 'Alignment', 'Finalize', 'Sheet'];
        labels.forEach((label, i) => {
            const dot = document.createElement('div');
            dot.className = 'step-dot';
            dot.title = label;
            dot.innerHTML = `<span class="dot"></span><span class="dot-label">${label}</span>`;
            indicators.appendChild(dot);
        });
    },

    goToStep(stepIndex) {
        this.state.currentStep = stepIndex;

        // Show/hide sections
        this.steps.forEach((id, i) => {
            const section = document.getElementById(id);
            section.classList.toggle('active', i === stepIndex);
        });

        // Update indicators
        document.querySelectorAll('.step-dot').forEach((dot, i) => {
            dot.classList.toggle('active', i === stepIndex);
            dot.classList.toggle('completed', i < stepIndex);
        });

        // Update nav buttons
        document.getElementById('btn-back').disabled = stepIndex === 0;
        document.getElementById('btn-next').disabled = true;
        document.getElementById('btn-next').style.display = stepIndex >= this.steps.length - 2 ? 'none' : '';
        document.getElementById('btn-back').style.display = stepIndex >= this.steps.length - 1 ? 'none' : '';

        // Step-specific setup
        switch (stepIndex) {
            case 0: // Method selection
                if (this.state.method) {
                    document.getElementById('btn-next').disabled = false;
                }
                break;
            case 1: // Abilities
                this.rollAbilities();
                break;
            case 2: // Race
                this.setupRaceStep();
                break;
            case 3: // Class
                this.setupClassStep();
                break;
            case 4: // Alignment
                this.setupAlignmentStep();
                break;
            case 5: // Finalize
                UI.renderFinalization();
                break;
            case 6: // Sheet - handled by generateFinalCharacter
                break;
        }
    },

    nextStep() {
        if (this.state.currentStep < this.steps.length - 1) {
            this.goToStep(this.state.currentStep + 1);
        }
    },

    prevStep() {
        if (this.state.currentStep > 0) {
            // Reset dependent state when going back
            if (this.state.currentStep === 3) this.state.className = null;
            if (this.state.currentStep === 4) this.state.alignment = null;
            if (this.state.currentStep === 2) this.state.race = null;

            this.goToStep(this.state.currentStep - 1);
        }
    },

    rollAbilities() {
        let result;
        switch (this.state.method) {
            case 1: result = Methods.methodI(); break;
            case 2: result = Methods.methodII(); break;
            case 3: result = Methods.methodIII(); break;
            case 4: result = Methods.methodIV(); break;
        }

        this.state.methodResult = result;
        this.state.abilities = null;

        if (result.method === 1 || result.method === 2) {
            UI.renderArrangeableScores(result);
        } else if (result.method === 3) {
            UI.renderFixedScores(result);
        } else if (result.method === 4) {
            UI.renderCharacterPicker(result);
        }
    },

    setupRaceStep() {
        if (!this.state.abilities) return;
        const availableRaces = Generator.getAvailableRaces(this.state.abilities);
        UI.renderRaceSelection(availableRaces);
        if (this.state.race) {
            const btn = document.querySelector(`.option-btn[data-race="${this.state.race}"]`);
            if (btn && !btn.disabled) {
                btn.click();
            }
        }
    },

    setupClassStep() {
        if (!this.state.abilities || !this.state.race) return;
        const adjustedAbilities = Generator.applyRacialAdjustments(this.state.abilities, this.state.race);
        const availableClasses = Generator.getAvailableClasses(adjustedAbilities, this.state.race);
        const availableMultiClasses = Generator.getAvailableMultiClasses(adjustedAbilities, this.state.race);
        UI.renderClassSelection(availableClasses, availableMultiClasses);
    },

    setupAlignmentStep() {
        if (!this.state.className) return;
        const availableAlignments = Generator.getAvailableAlignments(this.state.className);
        UI.renderAlignmentSelection(availableAlignments);
    },

    generateFinalCharacter() {
        const name = document.getElementById('char-name').value || 'Unnamed Adventurer';
        const sex = document.getElementById('char-sex').value;

        const char = Generator.buildCharacter({
            abilities: this.state.adjustedAbilities || this.state.abilities,
            race: this.state.race,
            className: this.state.className,
            alignment: this.state.alignment,
            name,
            sex
        });

        this.state.character = char;
        this.goToStep(6);
        UI.renderCharacterSheet(char);
    },

    reset() {
        this.state = {
            currentStep: 0,
            method: null,
            methodResult: null,
            abilities: null,
            adjustedAbilities: null,
            race: null,
            className: null,
            alignment: null,
            character: null
        };

        document.querySelectorAll('.method-card').forEach(c => c.classList.remove('selected'));
        document.getElementById('btn-next').style.display = '';
        document.getElementById('btn-back').style.display = '';
        this.goToStep(0);
    }
};

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => App.init());
