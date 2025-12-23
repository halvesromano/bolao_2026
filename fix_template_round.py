
content = """{% extends 'core/base.html' %}

{% block content %}
<ul class="nav nav-tabs mb-4" id="myTab" role="tablist">
    <li class="nav-item" role="presentation">
        <button class="nav-link active" id="upcoming-tab" data-bs-toggle="tab" data-bs-target="#upcoming" type="button">Próximos Jogos</button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="past-tab" data-bs-toggle="tab" data-bs-target="#past" type="button">Resultados</button>
    </li>
</ul>

<div class="tab-content" id="myTabContent">
    <!-- UPCOMING MATCHES -->
    <div class="tab-pane fade show active" id="upcoming">
        {% if upcoming %}
        <div class="row">
            {% for item in upcoming %}
            <div class="col-md-6 mb-4">
                <div class="card match-card h-100 {% if item.is_locked %}border-secondary bg-light{% else %}border-primary{% endif %}">
                    <div class="card-header text-center">
                        <span class="badge bg-dark mb-1">Rodada {{ item.match.round }}</span><br>
                        {{ item.match.date|date:"D, d/m - H:i" }}
                        {% if item.is_locked %}
                            <span class="badge bg-secondary ms-2">Encerrado</span>
                        {% else %}
                            <span class="badge bg-success ms-2">Aberto até {{ item.deadline|date:"H:i" }}</span>
                        {% endif %}
                    </div>
                    <div class="card-body text-center">
                        <h5>
                            <span class="fs-4">{{ item.match.home_team.flag_code }} {{ item.match.home_team.name }}</span>
                            <span class="mx-2">vs</span>
                            <span class="fs-4">{{ item.match.away_team.name }} {{ item.match.away_team.flag_code }}</span>
                        </h5>
                        
                        <form action="{% url 'submit_prediction' item.match.id %}" method="post" class="mt-3 row justify-content-center">
                            {% csrf_token %}
                            <div class="col-3">
                                <input type="number" name="home_score" class="form-control text-center text-dark" value="{{ item.prediction.home_score|default_if_none:'' }}" {% if item.is_locked %}disabled{% endif %} required placeholder="casa">
                            </div>
                            <div class="col-auto align-self-center">X</div>
                            <div class="col-3">
                                <input type="number" name="away_score" class="form-control text-center text-dark" value="{{ item.prediction.away_score|default_if_none:'' }}" {% if item.is_locked %}disabled{% endif %} required placeholder="fora">
                            </div>
                            {% if not item.is_locked %}
                            <div class="col-12 mt-2">
                                <button type="submit" class="btn btn-primary btn-sm">Salvar Palpite</button>
                            </div>
                            {% endif %}
                        </form>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
            <div class="alert alert-info">Nenhum jogo próximo agendado.</div>
        {% endif %}
    </div>

    <!-- PAST MATCHES -->
    <div class="tab-pane fade" id="past">
        {% if past %}
            <div class="list-group">
            {% for item in past %}
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <div class="fw-bold">
                            {{ item.match.home_team.name }} {{ item.match.home_score }} x {{ item.match.away_score }} {{ item.match.away_team.name }}
                        </div>
                        <small class="text-muted">Rodada {{ item.match.round }} - {{ item.match.date|date:"d/m/Y H:i" }}</small>
                    </div>
                    <div class="text-end">
                        {% if item.prediction %}
                            <div>Seu palpite: {{ item.prediction.home_score }} x {{ item.prediction.away_score }}</div>
                            <span class="badge bg-warning text-dark">+{{ item.prediction.points }} pontos</span>
                        {% else %}
                            <span class="badge bg-secondary">Sem palpite</span>
                        {% endif %}
                    </div>
                </div>
            {% endfor %}
            </div>
        {% else %}
            <div class="alert alert-info">Nenhum jogo finalizado ainda.</div>
        {% endif %}
    </div>
</div>
{% endblock %}
"""

with open(r'c:\Users\m753051\code\bolao_2026\core\templates\core\dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("File written successfully.")
