plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.samurai.supra"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.samurai.supra"
        minSdk = 26
        targetSdk = 35
        versionCode = 51
        versionName = "5.1.0"
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.16.0")
    implementation("androidx.activity:activity-ktx:1.10.1")
    implementation("androidx.camera:camera-core:1.6.1")
    implementation("androidx.camera:camera-camera2:1.6.1")
    implementation("androidx.camera:camera-lifecycle:1.6.1")
    implementation("androidx.camera:camera-view:1.6.1")
    implementation("androidx.webkit:webkit:1.14.0")
}
