/**
 * 1st Edition AD&D Character Generator - UI Rendering
 */

const UI = {
    /**
     * Render the ability score assignment interface for Methods I & II (arrangeable).
     */
    renderArrangeableScores(result) {
        const container = document.getElementById('ability-results');
        const totals = result.totals;

        let html = `<p class="method-label">${result.description}</p>`;

        // Show the roll details
        if (result.method === 1) {
            html += '<div class="roll-details"><h3>Your Rolls</h3><div class="roll-grid">';
            result.scores.forEach((s, i) => {
                html += `<div class="roll-box">
                    <span class="roll-num">#${i + 1}</span>
                    <span class="roll-dice">[${s.allRolls.join(', ')}]</span>
                    <span class="roll-dropped">drop ${s.allRolls[0]}</span>
                    <span class="roll-total">${s.total}</span>
                </div>`;
            });
            html += '</div></div>';
        } else if (result.method === 2) {
            html += '<div class="roll-details"><h3>All 12 Rolls</h3><div class="roll-grid twelve">';
            result.allScores.forEach((s, i) => {
                const isKept = result.bestSix.includes(s.total) &&
                    result.bestSix.filter(x => x === s.total).length >
                    result.allScores.slice(0, i).filter(x => result.bestSix.includes(x.total) && x.total === s.total).length;
                html += `<div class="roll-box ${result.totals.includes(s.total) ? 'kept' : 'dropped'}">
                    <span class="roll-dice">[${s.allRolls.join(', ')}]</span>
                    <span class="roll-total">${s.total}</span>
                </div>`;
            });
            html += '</div><p class="hint">Best 6 scores highlighted</p></div>';
        }

        html += '<div class="assign-section"><h3>Assign Scores to Abilities</h3>';
        html += '<p class="hint">Select a score for each ability from the dropdown.</p>';
        html += '<div class="assign-grid">';

        ABILITIES.forEach(ability => {
            html += `<div class="assign-row">
                <label>${ABILITY_LABELS[ability]}</label>
                <select class="score-select" data-ability="${ability}">
                    <option value="">-- Select --</option>
                    ${totals.map(t => `<option value="${t}">${t}</option>`).join('')}
                </select>
            </div>`;
        });

        html += '</div></div>';
        container.innerHTML = html;

        // Track used scores
        this._setupScoreAssignment(totals);
    },

    _setupScoreAssignment(totals) {
        const selects = document.querySelectorAll('.score-select');
        const updateSelects = () => {
            const used = {};
            const availableCounts = {};
            totals.forEach(t => { availableCounts[t] = (availableCounts[t] || 0) + 1; });

            selects.forEach(sel => {
                if (sel.value) {
                    used[sel.value] = (used[sel.value] || 0) + 1;
                }
            });

            selects.forEach(sel => {
                const currentVal = sel.value;
                const options = sel.querySelectorAll('option');
                options.forEach(opt => {
                    if (opt.value === '') return;
                    const val = opt.value;
                    const totalAvailable = availableCounts[val] || 0;
                    const totalUsed = used[val] || 0;
                    const isCurrentSelection = val === currentVal;
                    opt.disabled = !isCurrentSelection && totalUsed >= totalAvailable;
                });
            });

            // Enable next button only when all are assigned
            const allAssigned = Array.from(selects).every(s => s.value !== '');
            document.getElementById('btn-next').disabled = !allAssigned;

            if (allAssigned) {
                App.state.abilities = {};
                selects.forEach(s => {
                    App.state.abilities[s.dataset.ability] = parseInt(s.value);
                });
            }
        };

        selects.forEach(s => s.addEventListener('change', updateSelects));
    },

    /**
     * Render Method III results (fixed assignment).
     */
    renderFixedScores(result) {
        const container = document.getElementById('ability-results');

        let html = `<p class="method-label">${result.description}</p>`;
        html += '<div class="fixed-scores">';

        ABILITIES.forEach(ability => {
            const detail = result.details[ability];
            html += `<div class="fixed-score-row">
                <div class="ability-name">${ABILITY_LABELS[ability]}</div>
                <div class="ability-rolls">`;

            detail.allRolls.forEach(roll => {
                const isBest = roll.total === detail.best;
                html += `<span class="mini-roll ${isBest ? 'best' : ''}">${roll.total}</span>`;
            });

            html += `</div>
                <div class="ability-score">${detail.best}</div>
            </div>`;
        });

        html += '</div>';
        html += '<button class="btn btn-primary" id="btn-accept-scores">Accept These Scores</button>';
        html += ' <button class="btn btn-secondary" id="btn-reroll">Re-Roll</button>';
        container.innerHTML = html;

        document.getElementById('btn-accept-scores').addEventListener('click', () => {
            App.state.abilities = { ...result.abilities };
            document.getElementById('btn-next').disabled = false;
            document.getElementById('btn-next').click();
        });

        document.getElementById('btn-reroll').addEventListener('click', () => {
            App.rollAbilities();
        });
    },

    /**
     * Render Method IV results (pick a character).
     */
    renderCharacterPicker(result) {
        const container = document.getElementById('ability-results');

        let html = `<p class="method-label">${result.description}</p>`;
        html += '<div class="character-grid">';

        result.characters.forEach((char, i) => {
            html += `<div class="char-card" data-index="${i}">
                <h4>Character #${i + 1}</h4>
                <div class="char-stats">`;

            ABILITIES.forEach(ability => {
                html += `<div class="char-stat">
                    <span class="stat-abbrev">${ABILITY_ABBREV[ability]}</span>
                    <span class="stat-value">${char.abilities[ability]}</span>
                </div>`;
            });

            html += `</div>
                <div class="char-total">Total: ${char.total}</div>
            </div>`;
        });

        html += '</div>';
        html += '<button class="btn btn-secondary" id="btn-reroll-iv">Re-Generate All 12</button>';
        container.innerHTML = html;

        // Click to select a character
        document.querySelectorAll('.char-card').forEach(card => {
            card.addEventListener('click', () => {
                document.querySelectorAll('.char-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                const idx = parseInt(card.dataset.index);
                App.state.abilities = { ...result.characters[idx].abilities };
                document.getElementById('btn-next').disabled = false;
            });
        });

        document.getElementById('btn-reroll-iv').addEventListener('click', () => {
            App.rollAbilities();
        });
    },

    /**
     * Render race selection.
     */
    renderRaceSelection(availableRaces) {
        const container = document.getElementById('race-options');
        const infoPanel = document.getElementById('race-info');

        let html = '<div class="option-grid">';
        Object.keys(RACE_LABELS).forEach(race => {
            const available = availableRaces.includes(race);
            html += `<button class="option-btn ${available ? '' : 'disabled'}"
                data-race="${race}" ${available ? '' : 'disabled'}>
                <span class="option-name">${RACE_LABELS[race]}</span>
                ${!available ? '<span class="option-note">Requirements not met</span>' : ''}
            </button>`;
        });
        html += '</div>';
        container.innerHTML = html;

        // Show info on hover/click
        document.querySelectorAll('.option-btn[data-race]').forEach(btn => {
            btn.addEventListener('click', () => {
                if (btn.disabled) return;
                document.querySelectorAll('.option-btn[data-race]').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');

                const race = btn.dataset.race;
                App.state.race = race;

                // Show race info
                const adj = RACIAL_ADJUSTMENTS[race];
                const adjStr = ABILITIES
                    .filter(a => adj[a] !== 0)
                    .map(a => `${adj[a] > 0 ? '+' : ''}${adj[a]} ${ABILITY_ABBREV[a]}`)
                    .join(', ') || 'None';

                const limits = RACIAL_LIMITS[race];
                const limitsStr = ABILITIES
                    .map(a => `${ABILITY_ABBREV[a]}: ${limits[a][0]}-${limits[a][1]}`)
                    .join(', ');

                infoPanel.innerHTML = `
                    <h3>${RACE_LABELS[race]}</h3>
                    <p>${RACE_DESCRIPTIONS[race]}</p>
                    <p><strong>Adjustments:</strong> ${adjStr}</p>
                    <p><strong>Ability Ranges:</strong> ${limitsStr}</p>
                    <p><strong>Movement:</strong> ${RACIAL_MOVEMENT[race]}"</p>
                    <p><strong>Languages:</strong> ${RACIAL_LANGUAGES[race].join(', ')}</p>
                `;

                document.getElementById('btn-next').disabled = false;
            });
        });
    },

    /**
     * Render class selection.
     */
    renderClassSelection(availableClasses, availableMultiClasses) {
        const container = document.getElementById('class-options');
        const infoPanel = document.getElementById('class-info');

        let html = '<h3>Single Classes</h3><div class="option-grid">';
        Object.keys(CLASS_LABELS).forEach(cls => {
            const available = availableClasses.includes(cls);
            const reqs = CLASS_REQUIREMENTS[cls];
            const reqStr = Object.entries(reqs).map(([a, v]) => `${ABILITY_ABBREV[a]} ${v}`).join(', ');

            html += `<button class="option-btn ${available ? '' : 'disabled'}"
                data-class="${cls}" ${available ? '' : 'disabled'}>
                <span class="option-name">${CLASS_LABELS[cls]}</span>
                <span class="option-note">${available ? `Requires: ${reqStr}` : `Needs: ${reqStr}`}</span>
            </button>`;
        });
        html += '</div>';

        if (availableMultiClasses.length > 0) {
            html += '<h3>Multi-Classes</h3><div class="option-grid">';
            availableMultiClasses.forEach(mc => {
                const label = mc.split('/').map(c => CLASS_LABELS[c]).join(' / ');
                html += `<button class="option-btn" data-class="${mc}">
                    <span class="option-name">${label}</span>
                </button>`;
            });
            html += '</div>';
        }

        container.innerHTML = html;

        document.querySelectorAll('.option-btn[data-class]').forEach(btn => {
            btn.addEventListener('click', () => {
                if (btn.disabled) return;
                document.querySelectorAll('.option-btn[data-class]').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');

                const cls = btn.dataset.class;
                App.state.className = cls;

                // Show class info
                const isMulti = cls.includes('/');
                if (isMulti) {
                    const classes = cls.split('/');
                    const descriptions = classes.map(c => `<strong>${CLASS_LABELS[c]}:</strong> ${CLASS_DESCRIPTIONS[c]}`).join('<br>');
                    const levelLimits = classes.map(c =>
                        `${CLASS_LABELS[c]}: ${Generator.getLevelLimit(App.state.race, c)}`
                    ).join(', ');

                    infoPanel.innerHTML = `
                        <h3>${Generator.getClassLabel(cls)}</h3>
                        <p>${descriptions}</p>
                        <p><strong>Level Limits:</strong> ${levelLimits}</p>
                    `;
                } else {
                    const levelLimit = Generator.getLevelLimit(App.state.race, cls);
                    infoPanel.innerHTML = `
                        <h3>${CLASS_LABELS[cls]}</h3>
                        <p>${CLASS_DESCRIPTIONS[cls]}</p>
                        <p><strong>Hit Die:</strong> d${CLASS_HIT_DICE[cls]}${cls === 'ranger' ? ' (2d8 at level 1)' : ''}</p>
                        <p><strong>Level Limit:</strong> ${levelLimit}</p>
                    `;
                }

                document.getElementById('btn-next').disabled = false;
            });
        });
    },

    /**
     * Render alignment selection.
     */
    renderAlignmentSelection(availableAlignments) {
        const container = document.getElementById('alignment-options');
        const allAlignments = ['lg', 'ng', 'cg', 'ln', 'tn', 'cn', 'le', 'ne', 'ce'];

        let html = '<div class="alignment-grid">';
        allAlignments.forEach(al => {
            const available = availableAlignments.includes(al);
            html += `<button class="option-btn alignment-btn ${available ? '' : 'disabled'}"
                data-alignment="${al}" ${available ? '' : 'disabled'}>
                ${ALIGNMENT_LABELS[al]}
            </button>`;
        });
        html += '</div>';

        container.innerHTML = html;

        document.querySelectorAll('.alignment-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                if (btn.disabled) return;
                document.querySelectorAll('.alignment-btn').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                App.state.alignment = btn.dataset.alignment;
                document.getElementById('btn-next').disabled = false;
            });
        });
    },

    /**
     * Render the finalization step (name, sex, HP, gold preview).
     */
    renderFinalization() {
        const container = document.getElementById('finalize-results');
        const state = App.state;

        // Apply racial adjustments
        const adjustedAbilities = Generator.applyRacialAdjustments(state.abilities, state.race);
        state.adjustedAbilities = adjustedAbilities;

        // Show adjustments
        const adj = RACIAL_ADJUSTMENTS[state.race];
        const hasAdj = ABILITIES.some(a => adj[a] !== 0);

        let html = '<div class="finalize-form">';
        html += `<div class="form-row">
            <label for="char-name">Character Name</label>
            <input type="text" id="char-name" placeholder="Enter character name" value="">
        </div>`;
        html += `<div class="form-row">
            <label for="char-sex">Sex</label>
            <select id="char-sex">
                <option value="Male">Male</option>
                <option value="Female">Female</option>
            </select>
        </div>`;

        if (hasAdj) {
            html += '<div class="adjustments-table"><h3>Racial Adjustments Applied</h3><table>';
            html += '<tr><th>Ability</th><th>Base</th><th>Adj</th><th>Final</th></tr>';
            ABILITIES.forEach(a => {
                const adjVal = adj[a];
                if (adjVal !== 0) {
                    html += `<tr>
                        <td>${ABILITY_LABELS[a]}</td>
                        <td>${state.abilities[a]}</td>
                        <td class="${adjVal > 0 ? 'positive' : 'negative'}">${adjVal > 0 ? '+' : ''}${adjVal}</td>
                        <td><strong>${adjustedAbilities[a]}</strong></td>
                    </tr>`;
                }
            });
            html += '</table></div>';
        }

        html += `<div class="summary-preview">
            <h3>Character Summary</h3>
            <p><strong>Race:</strong> ${RACE_LABELS[state.race]}</p>
            <p><strong>Class:</strong> ${Generator.getClassLabel(state.className)}</p>
            <p><strong>Alignment:</strong> ${ALIGNMENT_LABELS[state.alignment]}</p>
        </div>`;

        html += '<div class="ability-preview"><h3>Final Ability Scores</h3><div class="score-display">';
        ABILITIES.forEach(a => {
            html += `<div class="score-box">
                <span class="score-label">${ABILITY_ABBREV[a]}</span>
                <span class="score-value">${adjustedAbilities[a]}</span>
            </div>`;
        });
        html += '</div></div>';

        html += `<button class="btn btn-primary" id="btn-generate">Generate Character!</button>`;
        html += '</div>';

        container.innerHTML = html;

        document.getElementById('btn-generate').addEventListener('click', () => {
            App.generateFinalCharacter();
        });

        // Hide next button on this step
        document.getElementById('btn-next').style.display = 'none';
    },

    /**
     * Render the final character sheet.
     */
    renderCharacterSheet(char) {
        const container = document.getElementById('character-sheet');

        let strDisplay = char.abilities.strength.toString();
        if (char.exceptionalStrength) {
            strDisplay = char.exceptionalStrength.label;
        }

        let html = `
        <div class="sheet">
            <div class="sheet-header">
                <h2 class="char-name">${char.name}</h2>
                <div class="char-title">${char.raceName} ${char.classLabel}</div>
                <div class="char-alignment">${char.alignmentLabel}</div>
            </div>

            <div class="sheet-columns">
                <div class="sheet-col">
                    <div class="sheet-section">
                        <h3>Ability Scores</h3>
                        <table class="ability-table">
                            <tr><td>Strength</td><td class="val">${strDisplay}</td></tr>
                            <tr><td>Intelligence</td><td class="val">${char.abilities.intelligence}</td></tr>
                            <tr><td>Wisdom</td><td class="val">${char.abilities.wisdom}</td></tr>
                            <tr><td>Dexterity</td><td class="val">${char.abilities.dexterity}</td></tr>
                            <tr><td>Constitution</td><td class="val">${char.abilities.constitution}</td></tr>
                            <tr><td>Charisma</td><td class="val">${char.abilities.charisma}</td></tr>
                        </table>
                    </div>

                    <div class="sheet-section">
                        <h3>Combat</h3>
                        <div class="combat-stats">
                            <div class="combat-stat">
                                <span class="combat-label">Hit Points</span>
                                <span class="combat-value">${char.hitPoints}</span>
                            </div>
                            <div class="combat-stat">
                                <span class="combat-label">Armor Class</span>
                                <span class="combat-value">${char.armorClass}</span>
                            </div>
                            <div class="combat-stat">
                                <span class="combat-label">THAC0</span>
                                <span class="combat-value">${char.thac0}</span>
                            </div>
                        </div>
                        <p class="hp-detail">`;

        if (char.hpDetails.isMultiClass) {
            html += `Multi-class: `;
            char.hpDetails.details.forEach((d, i) => {
                if (i > 0) html += ' + ';
                html += `${CLASS_LABELS[d.class]} ${d.rolls.join('+')}`;
            });
            html += ` = ${char.hpDetails.rawTotal} / ${char.hpDetails.numClasses} = ${char.hitPoints}`;
        } else {
            html += `${char.hpDetails.numDice}d${char.hpDetails.hitDie} [${char.hpDetails.rolls.join(', ')}]`;
            if (char.hpDetails.conBonus !== 0) {
                html += ` ${char.hpDetails.conBonus > 0 ? '+' : ''}${char.hpDetails.conBonus} (CON)`;
            }
            html += ` = ${char.hitPoints}`;
        }

        html += `</p>
                    </div>

                    <div class="sheet-section">
                        <h3>Saving Throws</h3>
                        <table class="saves-table">
                            <tr><td>Paralyzation/Poison/Death</td><td class="val">${char.savingThrows.paralyzation}</td></tr>
                            <tr><td>Petrification/Polymorph</td><td class="val">${char.savingThrows.petrification}</td></tr>
                            <tr><td>Rod/Staff/Wand</td><td class="val">${char.savingThrows.rodStaffWand}</td></tr>
                            <tr><td>Breath Weapon</td><td class="val">${char.savingThrows.breathWeapon}</td></tr>
                            <tr><td>Spell</td><td class="val">${char.savingThrows.spell}</td></tr>
                        </table>
                    </div>
                </div>

                <div class="sheet-col">
                    <div class="sheet-section">
                        <h3>Details</h3>
                        <table class="details-table">
                            <tr><td>Sex</td><td>${char.sex}</td></tr>
                            <tr><td>Age</td><td>${char.age} years</td></tr>
                            <tr><td>Height</td><td>${char.height}</td></tr>
                            <tr><td>Weight</td><td>${char.weight} lbs</td></tr>
                            <tr><td>Movement</td><td>${char.movement}"</td></tr>
                            <tr><td>Hit Die</td><td>${Generator.getHitDieLabel(char.className)}</td></tr>`;

        if (char.levelLimits) {
            html += `<tr><td>Level Limits</td><td>${char.levelLimits.map(l => `${l.class}: ${l.limit}`).join(', ')}</td></tr>`;
        } else {
            html += `<tr><td>Level Limit</td><td>${char.levelLimit}</td></tr>`;
        }

        html += `   <tr><td>Starting Gold</td><td>${char.gold} gp</td></tr>
                        </table>
                    </div>

                    <div class="sheet-section">
                        <h3>Languages</h3>
                        <p>${char.languages.join(', ')}</p>
                        <p class="hint">Additional language slots: ${char.additionalLanguageSlots}</p>
                    </div>`;

        // Thief skills
        if (char.thiefSkills) {
            html += `<div class="sheet-section">
                <h3>Thief Skills</h3>
                <table class="thief-table">`;
            for (const [skill, value] of Object.entries(char.thiefSkills)) {
                html += `<tr><td>${THIEF_SKILL_LABELS[skill]}</td><td class="val">${value}%</td></tr>`;
            }
            html += '</table></div>';
        }

        html += `
                    <div class="sheet-section">
                        <h3>Equipment</h3>
                        <p class="hint">Starting gold: ${char.gold} gp. Purchase equipment from the PHB.</p>
                        <div class="equipment-lines">
                            <div class="equip-line"></div>
                            <div class="equip-line"></div>
                            <div class="equip-line"></div>
                            <div class="equip-line"></div>
                            <div class="equip-line"></div>
                            <div class="equip-line"></div>
                        </div>
                    </div>

                    <div class="sheet-section">
                        <h3>Notes</h3>
                        <div class="notes-lines">
                            <div class="note-line"></div>
                            <div class="note-line"></div>
                            <div class="note-line"></div>
                            <div class="note-line"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>`;

        container.innerHTML = html;
    }
};
