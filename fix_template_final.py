
import os

file_path = r'c:\Users\m753051\code\bolao_2026\core\templates\core\all_predictions.html'

content = """{% extends 'core/base.html' %}

{% block content %}
<h2 class="mb-4 text-center">📊 Palpites da Galera</h2>

<div class="card shadow-sm mb-4">
    <div class="card-body">
        <form method="get" class="row g-3">
            <div class="col-md-3">
                <label class="form-label">Filtrar por Usuário</label>
                <select name="user" class="form-select" id="userFilter">
                    <option value="">Todos</option>
                    {% for u in users %}
                    <option value="{{ u.id }}" {% if request.GET.user|add:"0" == u.id %}selected{% endif %}>{{ u.first_name|default:u.username }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-3">
                <label class="form-label">Filtrar por Rodada</label>
                <select name="round" class="form-select" id="roundFilter">
                    <option value="">Todas</option>
                    {% for r in rounds %}
                    <option value="{{ r }}" {% if request.GET.round|add:"0" == r %}selected{% endif %}>{{ r }}ª Rodada</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-4">
                <label class="form-label">Filtrar por Jogo</label>
                <select name="match" class="form-select" id="matchFilter">
                    <option value="">Todos os jogos</option>
                    {% for m in matches %}
                    <option value="{{ m.id }}" data-round="{{ m.round }}" {% if request.GET.match|add:"0" == m.id %}selected{% endif %}>
                       R{{ m.round }}: {{ m.home_team.name }} x {{ m.away_team.name }}
                    </option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-2 d-flex align-items-end">
                <button type="submit" class="btn btn-primary w-100">Filtrar</button>
            </div>
        </form>
    </div>
</div>

<div class="table-responsive">
    <table class="table table-hover shadow-sm align-middle">
        <thead class="table-dark">
            <tr>
                <th scope="col">Data/Rodada</th>
                <th scope="col" class="text-center">Jogo</th>
                <th scope="col">Participante</th>
                <th scope="col" class="text-center">Palpite</th>
                <th scope="col" class="text-center">Resultado Oficial</th>
                <th scope="col" class="text-center">Pontos</th>
            </tr>
        </thead>
        <tbody>
            {% for pred in predictions %}
            <tr>
                <td>
                    <div class="fw-bold">{{ pred.match.date|date:"d/m H:i" }}</div>
                    <small class="text-muted">{{ pred.match.round }}ª Rodada</small>
                </td>
                <td class="text-center">
                    <span class="fw-bold">{{ pred.match.home_team.flag_code }} {{ pred.match.home_team.name }}</span>
                    x
                    <span class="fw-bold">{{ pred.match.away_team.name }} {{ pred.match.away_team.flag_code }}</span>
                </td>
                <td>{{ pred.user.first_name|default:pred.user.username }}</td>
                <td class="text-center">
                    <span class="badge bg-light text-dark border fs-6">
                        {{ pred.home_score }} x {{ pred.away_score }}
                    </span>
                </td>
                <td class="text-center">
                    {% if pred.match.is_finished %}
                    {{ pred.match.home_score }} x {{ pred.match.away_score }}
                    {% else %}
                    -
                    {% endif %}
                </td>
                <td class="text-center">
                    {% if pred.match.is_finished %}
                    <span class="badge bg-success">{{ pred.points }} pts</span>
                    {% else %}
                    <span class="text-muted">-</span>
                    {% endif %}
                </td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="6" class="text-center py-4">Nenhum palpite encontrado para os filtros selecionados (ou nenhum jogo encerrado).</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}

{% block scripts %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const roundSelect = document.getElementById('roundFilter');
        const matchSelect = document.getElementById('matchFilter');
        
        // Helper to get array of options since matches list is static in DOM
        // We will toggle their visibility/disabled state
        const matchOptions = Array.from(matchSelect.options);

        function updateMatchFilter() {
            const selectedRound = roundSelect.value;
            
            // If the currently selected match doesn't belong to the new round, reset it
            const currentMatchId = matchSelect.value;
            if (currentMatchId !== "") {
                const selectedOption = matchSelect.querySelector(`option[value="${currentMatchId}"]`);
                if (selectedOption && selectedRound !== "" && selectedOption.dataset.round !== selectedRound) {
                    matchSelect.value = "";
                }
            }

            if (selectedRound === "") {
                // If no round selected, disable match filter
                matchSelect.disabled = true;
                matchSelect.value = "";
            } else {
                matchSelect.disabled = false;
                
                // Show only matches for the selected round
                matchOptions.forEach(option => {
                    if (option.value === "") return; // "All games" option always visible if enabled
                    
                    if (option.dataset.round === selectedRound) {
                        option.hidden = false;
                        option.disabled = false;
                    } else {
                        option.hidden = true;
                        option.disabled = true;
                    }
                });
            }
        }

        // Initialize on load
        updateMatchFilter();

        // Listen for changes
        roundSelect.addEventListener('change', updateMatchFilter);
    });
</script>
{% endblock %}
"""

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Successfully overwrote {file_path}")
