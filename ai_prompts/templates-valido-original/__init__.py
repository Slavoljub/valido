
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inteligentna Analiza Tržišta</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        /* Opšti stilovi */
        body {
            background-color: #1c1c1e;
            color: #f8f9fa;
            font-family: 'Arial', sans-serif;
        }
        .navbar {
            background-color: #0d6efd;
        }
        .navbar-brand, .nav-link {
            color: #f8f9fa !important;
        }
        footer {
            background-color: #0d1117;
            color: #b3b3b3;
            padding: 10px;
            margin-top: 30px;
            border-radius: 8px;
            text-align: center;
        }
        .description {
            margin-top: 20px;
            padding: 20px;
            background-color: #2c2c2e;
            border-radius: 10px;
            text-align: center;
        }
        h1 {
            font-size: 2.5rem;
        }
        .grid-container {
            display: grid;
            grid-template-columns: 2fr 4fr;
            gap: 20px;
            margin-top: 30px;
        }
        .chat-box {
            background-color: #2c2c2e;
            padding: 20px;
            border-radius: 10px;
        }
        .chat-input-group {
            display: flex;
            align-items: center;
            border: 2px solid #0d6efd;
            border-radius: 8px;
            padding: 5px;
            background-color: #1c1c1e;
        }
        .chat-input-group input {
            flex: 1;
            background: none;
            border: none;
            outline: none;
            color: #f8f9fa;
            padding: 10px;
        }
        .chat-input-group button {
            background-color: #0d6efd;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
        }
        .chart-container {
            background-color: #2c2c2e;
            padding: 20px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        canvas {
            max-width: 100%;
            height: auto;
        }
        .chat-response {
            margin-top: 10px;
            background-color: #2c2c2e;
            border-radius: 8px;
            padding: 10px;
        }
        .chat-response p {
            margin-bottom: 10px;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg">
        <div class="container">
            <a class="navbar-brand" href="/">ValidoAI</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Početna</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/funkcionalnosti">Funkcionalnosti</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link active" href="/analiza">Analiza</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Opis -->
    <div class="container mt-5">
        <div class="description">
            <h1>Inteligentna Analiza Tržišta</h1>
            <p>ValidoAI omogućava pregled i analizu domaćih podataka. Postavite pitanje i dobijte vizuelni prikaz!</p>
        </div>

        <!-- Grid layout -->
        <div class="grid-container">
            <!-- Chat Box -->
            <div class="chat-box">
                <div class="chat-input-group">
                    <input type="text" id="chat-input" placeholder="Postavite pitanje o domaćem tržištu...">
                    <button id="send-button">Pošalji</button>
                </div>
                <div id="chat-response" class="chat-response"></div>
            </div>

            <!-- Grafikon -->
            <div class="chart-container">
                <canvas id="myChart"></canvas>
            </div>
        </div>
    </div>
    <footer>
        <p>&copy; 2025 ValidoAI. Sva prava zadržana.</p>
    </footer>
    <!-- Full-screen modal za analizu -->
<div class="modal fade modal-fullscreen" id="analysisModal" tabindex="-1" aria-labelledby="analysisModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title w-100 text-center" id="analysisModalLabel">Analiza i grafikon</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div id="modal-analysis-text" class="mb-4"></div>
                <div id="modal-analysis-chart" class="chart-container">
                    <canvas id="modalChart"></canvas>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zatvori</button>
                <button type="button" class="btn btn-primary" onclick="window.print()">Štampaj</button>
            </div>
        </div>
    </div>
</div>
<script>
const chatInput = document.getElementById('chat-input');
const sendButton = document.getElementById('send-button');
const chatResponse = document.getElementById('chat-response');
const ctx = document.getElementById('myChart').getContext('2d');
const footer = document.querySelector('footer'); // Footer za dugme
let myChart = null;
let lastResponseGiven = false; // Indikator za poslednji konkretan odgovor

// Dodaj modal u HTML (dinamički)
document.body.insertAdjacentHTML('beforeend', `
<div class="modal fade" id="printModal" tabindex="-1" aria-labelledby="printModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-fullscreen">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="printModalLabel">Štampa Analize</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        <h3 id="analysisText"></h3>
        <div id="chartContainerModal">
          <canvas id="chartForPrint"></canvas>
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zatvori</button>
        <button type="button" class="btn btn-primary" onclick="window.print()">Štampaj</button>
      </div>
    </div>
  </div>
</div>
`);

// Modal Chart Context
const chartModalCtx = document.getElementById('chartForPrint').getContext('2d');
let modalChart = null;

// Funkcija za prikaz poruke "Molimo vas, sačekajte..."
function showLoadingMessage() {
    chatResponse.innerHTML = `<p><em>Molimo vas, sačekajte...</em></p>`;
}

// Funkcija za efekat kucanja teksta
function simulateTypingEffect(text) {
    chatResponse.innerHTML = ''; // Prazni trenutni sadržaj
    let index = 0;

    const typingInterval = setInterval(() => {
        if (index < text.length) {
            chatResponse.innerHTML += text[index];
            index++;
        } else {
            clearInterval(typingInterval);
        }
    }, 50); // Brzina kucanja (50ms po karakteru)
}

// Funkcija za uklanjanje HTML tagova
function stripHtmlTags(text) {
    const div = document.createElement('div');
    div.innerHTML = text;
    return div.textContent || div.innerText || '';
}

// Formatira odgovor za čitljivost (dodaje razmake između pasusa)
function formatResponseText(text) {
    const strippedText = stripHtmlTags(text); // Uklanja HTML tagove
    return strippedText
        .split("\n")
        .map(line => `${line.trim()}\n\n`) // Dodaje dvostruki razmak između pasusa
        .join("");
}

// Ažuriranje grafikona s prilagođenim bojama
function updateChartWithColors(data) {
    const labels = data.map(item => item['Mesto']);
    const values = data.map(item => item['Prihodi']);

    if (myChart) {
        myChart.destroy(); // Uništava prethodni grafikon
    }

    myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Promet (u RSD)',
                data: values,
                backgroundColor: ['#ff4c4c', '#ff884d', '#ffcc4d', '#4dff88', '#4db8ff', '#994dff'],
                borderColor: ['#e63946', '#f77f00', '#e9c46a', '#2a9d8f', '#457b9d', '#6a4c93'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Prihodi po mestima za odabrani mesec'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Update chart for modal
    if (modalChart) {
        modalChart.destroy();
    }

    modalChart = new Chart(chartModalCtx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Promet (u RSD)',
                data: values,
                backgroundColor: ['#ff4c4c', '#ff884d', '#ffcc4d', '#4dff88', '#4db8ff', '#994dff'],
                borderColor: ['#e63946', '#f77f00', '#e9c46a', '#2a9d8f', '#457b9d', '#6a4c93'],
                borderWidth: 1
            }]
        }
    });
}

// Obrada klika na dugme "Pošalji"
sendButton.addEventListener('click', () => {
    const userMessage = chatInput.value.trim();

    if (!userMessage) {
        alert("Molimo vas da unesete pitanje!");
        return;
    }

    // Provera za pozdrave
    const greetings = ["zdravo", "ćao", "pozdrav", "hej", "dobar dan"];
    const lowerCaseMessage = userMessage.toLowerCase();

    if (greetings.some(greet => lowerCaseMessage.includes(greet))) {
        simulateTypingEffect("Zdravo! Kako vam mogu pomoći danas? Postavite pitanje o analizi domaćih podataka ili grafikonima.");
        return;
    }

    // Resetuje zastavicu za poslednji odgovor i prikazuje poruku "Molimo vas, sačekajte..."
    lastResponseGiven = false;
    showLoadingMessage();

    // Slanje zahteva ka backendu
    fetch('/api/analiza_chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            messages: [{ role: "user", content: userMessage }]
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.response && data.response !== "Nažalost, ne mogu da pronađem traženi mesec u vašoj poruci.") {
            const formattedText = formatResponseText(data.response);

            // Simulacija efekta kucanja za formatirani tekst
            simulateTypingEffect(formattedText);

            // Ako postoje podaci za grafikon, prikazuje ga
            if (data.data && Array.isArray(data.data)) {
                updateChartWithColors(data.data);
            }

            // Dodaj dugme za otvaranje modala
            footer.innerHTML = `
                <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#printModal">
                    Štampaj Analizu
                </button>
            `;

            // Update modal content
            document.getElementById('analysisText').textContent = formattedText;

            // Postavlja zastavicu da model može da odgovori na "Hvala"
            lastResponseGiven = true;
        } else {
            // Ako model ne prepozna relevantan mesec
            simulateTypingEffect("Molim vas, unesite tačnije pitanje. Ako imate pitanja o analizi, tu sam da pomognem!");
            lastResponseGiven = false; // Resetuje zastavicu jer nije bilo konkretnog odgovora
        }
    })
    .catch(error => {
        console.error("Greška u komunikaciji sa serverom:", error);
        simulateTypingEffect("Došlo je do greške u komunikaciji sa serverom.");
        lastResponseGiven = false;
    });
});

</script>
</body>
</html>