package com.lilith.agent

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

class MainActivity : AppCompatActivity() {

    private lateinit var consoleText: TextView
    private lateinit var inputEdit: EditText
    private lateinit var sendButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        consoleText = findViewById(R.id.consoleText)
        inputEdit = findViewById(R.id.inputEdit)
        sendButton = findViewById(R.id.sendButton)

        checkPermissions()

        sendButton.setOnClickListener {
            val input = inputEdit.text.toString()
            if (input.isNotBlank()) {
                consoleText.append("Sen: $input\n")
                inputEdit.text.clear()
                consoleText.append("Lilith: Henüz hazır değilim\n")
            }
        }
    }

    private fun checkPermissions() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)
            != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.RECORD_AUDIO), 100)
        }
    }
}
