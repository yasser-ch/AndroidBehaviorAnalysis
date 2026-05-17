package com.audit.behaviortestapp;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import java.util.concurrent.TimeUnit;

public class MainActivity extends AppCompatActivity {

    private static final String TAG       = "BehaviorApp";
    private static final String TAG_NET   = "BehaviorApp.Network";
    private static final String TAG_STOR  = "BehaviorApp.Storage";
    private static final String TAG_CRASH = "BehaviorApp.Crash";

    private static final String BASE_URL = "https://httpbin.org";

    private TextView tvStatus, tvLog;
    private ExecutorService executor;
    private Handler mainHandler;
    private OkHttpClient httpClient;
    private AtomicBoolean running = new AtomicBoolean(false);
    private StringBuilder logBuffer = new StringBuilder();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        tvStatus   = findViewById(R.id.tv_status);
        tvLog      = findViewById(R.id.tv_log);
        mainHandler = new Handler(Looper.getMainLooper());
        executor   = Executors.newFixedThreadPool(8);
        httpClient = new OkHttpClient.Builder()
                .connectTimeout(5, TimeUnit.SECONDS)
                .readTimeout(5, TimeUnit.SECONDS)
                .build();

        findViewById(R.id.btn_normal).setOnClickListener(v -> {
            stopAll();
            running.set(true);
            setStatus("Running: normal requests");
            executor.submit(this::doNormalRequests);
        });

        findViewById(R.id.btn_retry_loop).setOnClickListener(v -> {
            stopAll();
            running.set(true);
            setStatus("Running: retry loop");
            executor.submit(this::doRetryLoop);
        });

        findViewById(R.id.btn_request_spam).setOnClickListener(v -> {
            stopAll();
            running.set(true);
            setStatus("Running: request spam");
            for (int i = 0; i < 6; i++) {
                executor.submit(this::doRequestSpam);
            }
        });

        findViewById(R.id.btn_crash_storm).setOnClickListener(v -> {
            stopAll();
            running.set(true);
            setStatus("Running: crash storm");
            executor.submit(this::doCrashStorm);
        });

        findViewById(R.id.btn_slow_request).setOnClickListener(v -> {
            stopAll();
            running.set(true);
            setStatus("Running: slow / timeout");
            executor.submit(this::doSlowRequest);
        });

        findViewById(R.id.btn_stop).setOnClickListener(v -> {
            stopAll();
            setStatus("Stopped");
        });

        log("App started. Ready.");
        Log.i(TAG, "BehaviorTestApp started — profiler session ready");
    }

    private void doNormalRequests() {
        while (running.get()) {
            try {
                long start = System.currentTimeMillis();
                Request req = new Request.Builder()
                        .url(BASE_URL + "/get")
                        .build();
                Response resp = httpClient.newCall(req).execute();
                long ms = System.currentTimeMillis() - start;
                int code = resp.code();
                resp.close();

                // JSON Structured Log
                String logEntry = String.format("{\"tag\":\"%s\", \"latency\":%d, \"status\":%d}", TAG_NET, ms, code);
                Log.i(TAG, logEntry);

                log("[NET] GET /get → " + code + " (" + ms + "ms)");
                writeToFile("normal_requests.log", "GET /get → " + code + " in " + ms + "ms");

                Thread.sleep(3000);
            } catch (Exception e) {
                String logEntry = String.format("{\"tag\":\"%s\", \"latency\":0, \"status\":500}", TAG_NET);
                Log.w(TAG, logEntry);
                log("[ERR] " + e.getMessage());
            }
        }
    }

    private void doRetryLoop() {
        int attempt = 0;
        while (running.get()) {
            attempt++;
            try {
                Request req = new Request.Builder()
                        .url(BASE_URL + "/status/401")
                        .build();
                Response resp = httpClient.newCall(req).execute();
                int code = resp.code();
                resp.close();

                // JSON Structured Log (is_retry flag)
                String logEntry = String.format("{\"tag\":\"%s\", \"status\":%d, \"is_retry\":true}", TAG_NET, code);
                Log.w(TAG, logEntry);

                log("[RETRY] attempt #" + attempt + " → " + code);
                Thread.sleep(200);
            } catch (Exception e) {
                String logEntry = String.format("{\"tag\":\"%s\", \"status\":500, \"is_retry\":true}", TAG_NET);
                Log.e(TAG, logEntry);
                log("[ERR] retry exception: " + e.getMessage());
            }
        }
    }

    private void doRequestSpam() {
        int count = 0;
        while (running.get()) {
            count++;
            try {
                long start = System.currentTimeMillis();
                Request req = new Request.Builder()
                        .url(BASE_URL + "/get?req=" + count)
                        .build();
                Response resp = httpClient.newCall(req).execute();
                long ms = System.currentTimeMillis() - start;
                resp.close();

                // JSON Structured Log
                String logEntry = String.format("{\"tag\":\"%s\", \"latency\":%d, \"status\":200}", TAG_NET, ms);
                Log.w(TAG, logEntry);

                log("[SPAM] #" + count + " (" + ms + "ms)");
            } catch (Exception e) {
                String logEntry = String.format("{\"tag\":\"%s\", \"latency\":0, \"status\":500}", TAG_NET);
                Log.e(TAG, logEntry);
                log("[ERR] spam: " + e.getMessage());
            }
        }
    }

    private void doCrashStorm() {
        int count = 0;
        while (running.get()) {
            count++;
            try {
                // JSON Structured Log (is_crash flag)
                String logEntry = String.format("{\"tag\":\"%s\", \"is_crash\":true}", TAG_CRASH);
                Log.e(TAG, logEntry);

                writeToFile("crash_log.txt", "Crash #" + count + ": NullPointerException at LoginActivity.java:42");

                try {
                    String s = null;
                    s.length();
                } catch (NullPointerException e) {
                    log("[CRASH] NPE #" + count + " caught");
                }

                String storLog = String.format("{\"tag\":\"%s\"}", TAG_STOR);
                Log.d(TAG, storLog);
                Thread.sleep(500);
            } catch (Exception e) {
                Log.e(TAG_CRASH, "Crash storm error: " + e.getMessage());
            }
        }
    }

    private void doSlowRequest() {
        int count = 0;
        while (running.get()) {
            count++;
            try {
                long start = System.currentTimeMillis();
                Request req = new Request.Builder()
                        .url(BASE_URL + "/delay/10")
                        .build();
                log("[SLOW] request #" + count + " sent...");

                Response resp = httpClient.newCall(req).execute();
                long ms = System.currentTimeMillis() - start;

                String logEntry = String.format("{\"tag\":\"%s\", \"latency\":%d, \"status\":%d}", TAG_NET, ms, resp.code());
                Log.w(TAG, logEntry);
                resp.close();
            } catch (Exception e) {
                // JSON Structured Log (Timeout = 408)
                String logEntry = String.format("{\"tag\":\"%s\", \"status\":408, \"latency\":0}", TAG_NET);
                Log.e(TAG, logEntry);

                log("[TIMEOUT] #" + count + " → " + e.getMessage());
            }
            try { Thread.sleep(1000); } catch (InterruptedException ignored) {}
        }
    }

    private void stopAll() {
        running.set(false);
        log("--- stopped ---");
        Log.i(TAG, "All scenarios stopped");
    }

    private void setStatus(String s) {
        mainHandler.post(() -> tvStatus.setText("Status: " + s));
    }

    private void log(String msg) {
        mainHandler.post(() -> {
            logBuffer.insert(0, msg + "\n");
            if (logBuffer.length() > 3000) logBuffer.setLength(3000);
            tvLog.setText(logBuffer.toString());
        });
    }

    private void writeToFile(String filename, String content) {
        try {
            File file = new File(getFilesDir(), filename);
            FileWriter fw = new FileWriter(file, true);
            fw.write(System.currentTimeMillis() + " | " + content + "\n");
            fw.close();

            // JSON Structured Log for Storage Write
            String logEntry = String.format("{\"tag\":\"%s\"}", TAG_STOR);
            Log.d(TAG, logEntry);
        } catch (IOException e) {
            Log.e(TAG, "File write failed: " + e.getMessage());
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        running.set(false);
        executor.shutdownNow();
    }
}