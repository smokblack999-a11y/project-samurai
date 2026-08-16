package com.samurai.supra

import android.Manifest
import android.app.Activity
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.os.Bundle
import android.webkit.CookieManager
import android.webkit.JavascriptInterface
import android.webkit.MimeTypeMap
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.FrameLayout
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.FileInputStream
import java.net.HttpURLConnection
import java.net.URL
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

class MainActivity : Activity() {
    private lateinit var web: WebView
    private lateinit var cameraExecutor: ExecutorService
    private var imageCapture: ImageCapture? = null
    private var cameraRoot: FrameLayout? = null

    private val cameraPermission = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) openCameraNative()
        else toast("Camera permission denied")
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        cameraExecutor = Executors.newSingleThreadExecutor()
        web = buildWebView()
        setContentView(web)
    }

    private fun buildWebView(): WebView = WebView(this).apply {
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.mediaPlaybackRequiresUserGesture = false
        settings.allowFileAccess = false
        settings.allowContentAccess = false
        settings.setSupportZoom(false)
        CookieManager.getInstance().setAcceptCookie(true)
        webViewClient = SupraWebViewClient()
        setDownloadListener { url, userAgent, contentDisposition, mimeType, _ ->
            downloadIntoPrivateTelegramStorage(url, userAgent, contentDisposition, mimeType)
        }
        addJavascriptInterface(SupraBridge(), "SupraAndroid")
        loadUrl("file:///android_asset/index.html")
    }

    private fun mediaDir(): File = File(filesDir, "media").apply { mkdirs() }
    private fun telegramDir(): File = File(filesDir, "telegram").apply { mkdirs() }

    private fun openCameraNative() {
        if (cameraRoot != null) return
        val root = FrameLayout(this)
        cameraRoot = root
        val preview = PreviewView(this)
        val capture = Button(this).apply {
            text = "CAPTURE"
            setOnClickListener { capturePhoto() }
        }
        val close = Button(this).apply {
            text = "CLOSE"
            setOnClickListener { closeCamera() }
        }

        root.addView(preview, FrameLayout.LayoutParams(-1, -1))
        val captureLp = FrameLayout.LayoutParams(420, 140).apply {
            gravity = android.view.Gravity.BOTTOM or android.view.Gravity.CENTER_HORIZONTAL
            bottomMargin = 40
        }
        root.addView(capture, captureLp)
        val closeLp = FrameLayout.LayoutParams(260, 120).apply {
            gravity = android.view.Gravity.TOP or android.view.Gravity.END
            topMargin = 40
            rightMargin = 20
        }
        root.addView(close, closeLp)
        setContentView(root)

        val future = ProcessCameraProvider.getInstance(this)
        future.addListener({
            val provider = future.get()
            val previewUseCase = Preview.Builder().build().also {
                it.surfaceProvider = preview.surfaceProvider
            }
            imageCapture = ImageCapture.Builder()
                .setCaptureMode(ImageCapture.CAPTURE_MODE_MAXIMIZE_QUALITY)
                .build()
            provider.unbindAll()
            provider.bindToLifecycle(
                this,
                CameraSelector.DEFAULT_BACK_CAMERA,
                previewUseCase,
                imageCapture
            )
        }, ContextCompat.getMainExecutor(this))
    }

    private fun capturePhoto() {
        val capture = imageCapture ?: return
        val name = "IMG_" + SimpleDateFormat(
            "yyyyMMdd_HHmmss_SSS",
            Locale.US
        ).format(Date()) + ".jpg"
        val file = File(mediaDir(), name)
        val output = ImageCapture.OutputFileOptions.Builder(file).build()

        capture.takePicture(output, cameraExecutor, object : ImageCapture.OnImageSavedCallback {
            override fun onError(exc: ImageCaptureException) {
                runOnUiThread { toast("Capture failed: ${exc.message ?: "unknown"}") }
            }

            override fun onImageSaved(result: ImageCapture.OutputFileResults) {
                runOnUiThread {
                    toast("Saved inside SUPRA")
                    closeCamera()
                    web.evaluateJavascript("window.SupraUI && window.SupraUI.refreshGallery()", null)
                }
            }
        })
    }

    private fun closeCamera() {
        imageCapture = null
        cameraRoot = null
        setContentView(web)
    }

    private fun downloadIntoPrivateTelegramStorage(
        url: String,
        userAgent: String?,
        contentDisposition: String?,
        mimeType: String?
    ) {
        cameraExecutor.execute {
            var connection: HttpURLConnection? = null
            try {
                connection = (URL(url).openConnection() as HttpURLConnection).apply {
                    requestMethod = "GET"
                    instanceFollowRedirects = true
                    setRequestProperty("User-Agent", userAgent ?: "Mozilla/5.0")
                    val cookies = CookieManager.getInstance().getCookie(url)
                    if (!cookies.isNullOrBlank()) setRequestProperty("Cookie", cookies)
                }
                connection.connect()
                if (connection.responseCode !in 200..299) throw IllegalStateException("HTTP ${connection.responseCode}")
                val ext = MimeTypeMap.getSingleton().getExtensionFromMimeType(mimeType ?: "")
                    ?.let { ".${it}" } ?: ""
                val safeName = extractFilename(contentDisposition)?.replace(Regex("[^A-Za-z0-9._-]"), "_")
                    ?.take(100)
                    ?: "TG_${System.currentTimeMillis()}$ext"
                val target = uniqueFile(telegramDir(), safeName)
                connection.inputStream.use { input -> target.outputStream().use { output -> input.copyTo(output) } }
                runOnUiThread { toast("Telegram file saved privately") }
            } catch (e: Exception) {
                runOnUiThread { toast("Telegram download failed: ${e.message}") }
            } finally {
                connection?.disconnect()
            }
        }
    }

    private fun extractFilename(contentDisposition: String?): String? =
        Regex("filename\\*?=(?:UTF-8'')?\\\"?([^\\\";]+)", RegexOption.IGNORE_CASE)
            .find(contentDisposition ?: "")?.groupValues?.getOrNull(1)

    private fun uniqueFile(dir: File, name: String): File {
        val base = File(dir, name)
        if (!base.exists()) return base
        val stem = base.nameWithoutExtension
        val ext = if (base.extension.isBlank()) "" else ".${base.extension}"
        var i = 1
        while (true) {
            val candidate = File(dir, "${stem}_$i$ext")
            if (!candidate.exists()) return candidate
            i++
        }
    }

    private fun toast(message: String) = Toast.makeText(this, message, Toast.LENGTH_SHORT).show()

    inner class SupraBridge {
        @JavascriptInterface
        fun openCamera() {
            runOnUiThread {
                if (ContextCompat.checkSelfPermission(this@MainActivity, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) {
                    openCameraNative()
                } else {
                    cameraPermission.launch(Manifest.permission.CAMERA)
                }
            }
        }

        @JavascriptInterface
        fun listMedia(): String {
            val arr = JSONArray()
            mediaDir().listFiles()
                ?.filter { it.isFile }
                ?.sortedByDescending { it.lastModified() }
                ?.forEach { file ->
                    arr.put(JSONObject().apply {
                        put("name", file.name)
                        put("size", file.length())
                        put("uri", "supra-media://${file.name}")
                        put("modified", file.lastModified())
                    })
                }
            return arr.toString()
        }

        @JavascriptInterface
        fun listTelegramFiles(): String {
            val arr = JSONArray()
            telegramDir().listFiles()?.filter { it.isFile }?.sortedByDescending { it.lastModified() }?.forEach {
                arr.put(JSONObject().apply {
                    put("name", it.name)
                    put("size", it.length())
                    put("uri", "supra-telegram://${it.name}")
                    put("modified", it.lastModified())
                })
            }
            return arr.toString()
        }

        @JavascriptInterface
        fun telegramUrl(): String = "https://web.telegram.org/k/"

        @JavascriptInterface
        fun runtimeStatus(): String = JSONObject().apply {
            put("version", "5.1.0")
            put("privateMedia", true)
            put("camera", true)
            put("telegramWeb", true)
            put("tdlib", false)
        }.toString()
    }

    private inner class SupraWebViewClient : WebViewClient() {
        override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
            return false
        }

        override fun shouldInterceptRequest(view: WebView, request: WebResourceRequest): WebResourceResponse? {
            return privateResource(request.url.toString()) ?: super.shouldInterceptRequest(view, request)
        }

        override fun shouldInterceptRequest(view: WebView, url: String): WebResourceResponse? {
            return privateResource(url) ?: super.shouldInterceptRequest(view, url)
        }

        private fun privateResource(uri: String): WebResourceResponse? {
            val prefix = when {
                uri.startsWith("supra-media://") -> "media"
                uri.startsWith("supra-telegram://") -> "telegram"
                else -> return null
            }
            val rawName = uri.substringAfter("://").substringBefore('?')
            val name = java.net.URLDecoder.decode(rawName, "UTF-8")
            if (name.contains("/") || name.contains("\\") || name.contains("..")) return null
            val file = File(if (prefix == "media") mediaDir() else telegramDir(), name)
            if (!file.exists() || !file.isFile) return null
            val mime = MimeTypeMap.getSingleton().getMimeTypeFromExtension(file.extension.lowercase())
                ?: "application/octet-stream"
            return WebResourceResponse(mime, "UTF-8", FileInputStream(file))
        }
    }

    override fun onBackPressed() {
        if (cameraRoot != null) closeCamera()
        else if (web.canGoBack()) web.goBack()
        else super.onBackPressed()
    }

    override fun onDestroy() {
        imageCapture = null
        cameraExecutor.shutdown()
        super.onDestroy()
    }
}
