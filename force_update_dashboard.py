
import os

file_path = r'c:\Users\m753051\code\bolao_2026\core\templates\core\dashboard.html'

content = """{% extends 'core/base.html' %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <!-- Round Selector -->
    <form method="get" class="d-flex align-items-center">
        <label for="round" class="me-2 fw-bold">Rodada:</label>
        <select name="round" id="round" class="form-select form-select-sm" onchange="this.form.submit()"
            style="width: auto;">
            {% for r in rounds %}
            <option value="{{ r }}" {% if r == current_round %}selected{% endif %}>{{ r }}</option>
            {% endfor %}
        </select>
    </form>
</div>

<ul class="nav nav-tabs mb-4" id="myTab" role="tablist">
    <li class="nav-item" role="presentation">
        <button class="nav-link active" id="upcoming-tab" data-bs-toggle="tab" data-bs-target="#upcoming"
            type="button">Jogos</button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="past-tab" data-bs-toggle="tab" data-bs-target="#past"
            type="button">Resultados</button>
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
                        <div class="d-flex justify-content-center align-items-center mb-3">
                            <div class="text-center px-3" style="width: 45%;">
                                {% if item.match.home_team.logo %}
                                <img src="{{ item.match.home_team.logo.url }}" alt="{{ item.match.home_team.name }}"
                                    style="height: 50px; max-width: 100%;">
                                {% else %}
                                <span class="fs-1">{{ item.match.home_team.flag_code }}</span>
                                {% endif %}
                                <div class="fw-bold mt-1">{{ item.match.home_team.name }}</div>
                            </div>

                            <div class="fs-4 fw-bold text-muted">X</div>

                            <div class="text-center px-3" style="width: 45%;">
                                {% if item.match.away_team.logo %}
                                <img src="{{ item.match.away_team.logo.url }}" alt="{{ item.match.away_team.name }}"
                                    style="height: 50px; max-width: 100%;">
                                {% else %}
                                <span class="fs-1">{{ item.match.away_team.flag_code }}</span>
                                {% endif %}
                                <div class="fw-bold mt-1">{{ item.match.away_team.name }}</div>
                            </div>
                        </div>

                        <form action="{% url 'submit_prediction' item.match.id %}" method="post" class="mt-3 row justify-content-center">
                            {% csrf_token %}
                            <div class="col-3">
                                <input type="number" name="home_score" class="form-control text-center text-dark"
                                    value="{{ item.prediction.home_score|default_if_none:'' }}" {% if item.is_locked %}disabled{% endif %} required placeholder="casa">
                            </div>
                            <div class="col-auto align-self-center">X</div>
                            <div class="col-3">
                                <input type="number" name="away_score" class="form-control text-center text-dark"
                                    value="{{ item.prediction.away_score|default_if_none:'' }}" {% if item.is_locked %}disabled{% endif %} required placeholder="fora">
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
                    <div class="fw-bold d-flex align-items-center">
                        {% if item.match.home_team.logo %}
                        <img src="{{ item.match.home_team.logo.url }}" style="height: 20px; margin-right: 5px;">
                        {% else %}
                        {{ item.match.home_team.flag_code }}
                        {% endif %}
                        {{ item.match.home_team.name }} {{ item.match.home_score }} x {{ item.match.away_score }} {{ item.match.away_team.name }}
                        {% if item.match.away_team.logo %}
                        <img src="{{ item.match.away_team.logo.url }}" style="height: 20px; margin-left: 5px;">
                        {% else %}
                        {{ item.match.away_team.flag_code }}
                        {% endif %}
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

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Force updated {file_path}")
