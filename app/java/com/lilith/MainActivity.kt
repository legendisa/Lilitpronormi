package com.lilith.agent

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import kotlinx.coroutines.*

class MainActivity : AppCompatActivity() {

    private lateinit var consoleText: TextView
    private lateinit var inputEdit: EditText
    private lateinit var sendButton: Button
    private lateinit var voiceButton: Button
    private lateinit var accessibilityButton: Button
    
    private lateinit var lilithCore: PythonObject
    private val mainScope = CoroutineScope(Dispatchers.Main + Job())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        initViews()
        checkPermissions()
        initPython()
        checkAccessibilityPermission()
    }

    private fun initViews() {
        consoleText = findViewById(R.id.consoleText)
        inputEdit = findViewById(R.id.inputEdit)
        sendButton = findViewById(R.id.sendButton)
        voiceButton = findViewById(R.id.voiceButton)
        accessibilityButton = findViewById(R.id.accessibilityButton)

        sendButton.setOnClickListener {
            val input = inputEdit.text.toString()
            if (input.isNotBlank()) {
                processCommand(input)
                inputEdit.text.clear()
            }
        }

        voiceButton.setOnClickListener {
            startVoiceRecognition()
        }

        accessibilityButton.setOnClickListener {
            startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
        }
    }

    private fun checkPermissions() {
        val permissions = mutableListOf<String>()
        
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)
            != PackageManager.PERMISSION_GRANTED) {
            permissions.add(Manifest.permission.RECORD_AUDIO)
        }
        
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE)
            != PackageManager.PERMISSION_GRANTED) {
            permissions.add(Manifest.permission.WRITE_EXTERNAL_STORAGE)
        }
        
        if (permissions.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, permissions.toTypedArray(), 100)
        }
    }

    private fun checkAccessibilityPermission() {
        val service = android.content.ComponentName(this, LilithAccessibilityService::class.java)
        val enabledServices = Settings.Secure.getString(
            contentResolver,
            Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
        )
        if (!enabledServices?.contains(service.flattenToString()) == true) {
            AlertDialog.Builder(this)
                .setTitle("Erişilebilirlik İzni Gerekli")
                .setMessage("Lilith'in ekranı okuması ve kontrol etmesi için erişilebilirlik iznini verin.")
                .setPositiveButton("Ayarlara Git") { _, _ ->
                    startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
                }
                .setNegativeButton("Sonra", null)
                .show()
        }
    }

    private fun initPython() {
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }
        
        val py = Python.getInstance()
        val module = py.getModule("lilith_core")
        lilithCore = module.callAttr("LilithCore", this)
        
        addToConsole("🦇 Lilith başlatıldı. 49 özellik aktif.")
    }

    private fun processCommand(command: String) {
        addToConsole("👤 Sen: $command")
        
        mainScope.launch {
            val response = withContext(Dispatchers.IO) {
                lilithCore.callAttr("process_command", command).toString()
            }
            addToConsole("🦇 Lilith: $response")
            speakResponse(response)
        }
    }

    private fun startVoiceRecognition() {
        addToConsole("🎤 Dinliyorum...")
        
        mainScope.launch {
            val recognizedText = withContext(Dispatchers.IO) {
                lilithCore.callAttr("listen_to_me").toString()
            }
            
            if (recognizedText.isNotBlank()) {
                processCommand(recognizedText)
            } else {
                addToConsole("⚠️ Anlaşılmadı.")
            }
        }
    }

    private fun speakResponse(text: String) {
        try {
            lilithCore.callAttr("speak", text)
        } catch (e: Exception) { }
    }

    private fun addToConsole(message: String) {
        runOnUiThread {
            consoleText.append("$message\n")
        }
    }
}
