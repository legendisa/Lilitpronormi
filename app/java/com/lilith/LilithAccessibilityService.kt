package com.lilith.agent

import android.accessibilityservice.AccessibilityService
import android.view.accessibility.AccessibilityEvent

class LilithAccessibilityService : AccessibilityService() {
    
    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // Ekran değiştiğinde burası çalışır
    }
    
    override fun onInterrupt() {
        // Servis kesintiye uğradığında
    }
    
    fun getScreenText(): String {
        val root = rootInActiveWindow
        return root?.text?.toString() ?: ""
    }
    
    fun performBack(): Boolean {
        return performGlobalAction(GLOBAL_ACTION_BACK)
    }
    
    fun performHome(): Boolean {
        return performGlobalAction(GLOBAL_ACTION_HOME)
    }
}
