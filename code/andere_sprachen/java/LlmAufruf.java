// LLM-Aufruf in Java – entspricht lab01/hallo_llm.py (Python)
// Nur Standardbibliothek (java.net.http, ab Java 11). Start ohne Kompilieren (ab Java 11):
//   java LlmAufruf.java "Ihre Frage"
// Konfiguration über Umgebungsvariablen (wie .env): LLM_BASE_URL, LLM_API_KEY, LLM_MODEL, LLM_REASONING_EFFORT

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class LlmAufruf {

    static String env(String name, String standard) {
        String wert = System.getenv(name);
        return (wert == null || wert.isBlank()) ? standard : wert;
    }

    // JSON-Text sicher in Anführungszeichen setzen (ohne Zusatzbibliothek)
    static String json(String text) {
        return "\"" + text.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n") + "\"";
    }

    public static void main(String[] args) throws Exception {
        String basis = env("LLM_BASE_URL", "http://localhost:11434/v1");
        String modell = env("LLM_MODEL", "qwen3.5:4b");
        String frage = args.length > 0 ? args[0] : "Erkläre in zwei Sätzen, was ein Sprachmodell ist.";
        String denken = env("LLM_REASONING_EFFORT", "");

        String body = "{\"model\": " + json(modell)
                + (denken.isEmpty() ? "" : ", \"reasoning_effort\": " + json(denken))
                + ", \"messages\": [{\"role\": \"user\", \"content\": " + json(frage) + "}]}";

        HttpRequest anfrage = HttpRequest.newBuilder(URI.create(basis + "/chat/completions"))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + env("LLM_API_KEY", "ollama"))
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();

        HttpResponse<String> antwort = HttpClient.newHttpClient().send(anfrage, HttpResponse.BodyHandlers.ofString());
        // Für den Unterricht reicht die rohe JSON-Antwort; zum Auslesen eignet sich z. B. die Bibliothek Jackson oder Gson.
        System.out.println(antwort.body());
    }
}
