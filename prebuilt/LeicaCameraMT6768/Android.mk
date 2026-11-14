# Leica Camera for MT6768, release 1.0.1, maintained by MrShockWAVEog.
LOCAL_PATH := $(call my-dir)

ifneq ($(filter lancelot galahad merlin merlinx merlinnfc,$(TARGET_DEVICE)),)

leica_jni_files := $(notdir $(wildcard $(LOCAL_PATH)/lib/arm64/*.so))
leica_jni_modules := $(addprefix LeicaMT6768_,$(basename $(leica_jni_files)))

include $(CLEAR_VARS)
LOCAL_MODULE := LeicaCameraMT6768
LOCAL_MODULE_CLASS := APPS
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE_SUFFIX := .apk
LOCAL_INSTALLED_MODULE_STEM := LeicaCamera.apk
LOCAL_SRC_FILES := LeicaCamera.apk
LOCAL_CERTIFICATE := PRESIGNED
LOCAL_PRIVILEGED_MODULE := true
LOCAL_MODULE_PATH := $(TARGET_OUT_APPS_PRIVILEGED)
LOCAL_MULTILIB := 64
LOCAL_DEX_PREOPT := false
# Copy the release-signed APK byte for byte, including its compressed DEX.
# Repacking or re-signing would change the tested APK/update identity.
LOCAL_REPLACE_PREBUILT_APK_INSTALLED := $(LOCAL_PATH)/LeicaCamera.apk
LOCAL_OVERRIDES_PACKAGES := Aperture ApertureOverlayMerlinx ApertureOverlayLancelot
LOCAL_REQUIRED_MODULES := \
    $(leica_jni_modules) \
    LeicaCameraMT6768Overlay \
    privapp-permissions-leica-mt6768 \
    leica-mt6768-hiddenapi
include $(BUILD_PREBUILT)

# Keep JNI private to the app, at the same paths used by the working module.
# These names must never replace system-wide libc++, libion or libjpeg.
define leica_app_jni
include $$(CLEAR_VARS)
LOCAL_MODULE := LeicaMT6768_$(basename $(1))
LOCAL_MODULE_CLASS := SHARED_LIBRARIES
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE_SUFFIX := .so
LOCAL_MODULE_STEM := $(basename $(1))
LOCAL_SRC_FILES := lib/arm64/$(1)
LOCAL_MODULE_PATH := $$(TARGET_OUT_APPS_PRIVILEGED)/LeicaCameraMT6768/lib/arm64
LOCAL_MULTILIB := 64
LOCAL_STRIP_MODULE := false
# App-bundled JNI resolves inside the app's linker namespace at runtime.
LOCAL_CHECK_ELF_FILES := false
LOCAL_SYSTEM_SHARED_LIBRARIES :=
include $$(BUILD_PREBUILT)
endef
$(foreach library,$(leica_jni_files),$(eval $(call leica_app_jni,$(library))))

include $(CLEAR_VARS)
LOCAL_MODULE := LeicaCameraMT6768Overlay
LOCAL_MODULE_CLASS := APPS
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE_SUFFIX := .apk
LOCAL_SRC_FILES := LeicaCameraMT6768Overlay.apk
LOCAL_CERTIFICATE := PRESIGNED
LOCAL_PRODUCT_MODULE := true
LOCAL_IS_RUNTIME_RESOURCE_OVERLAY := true
LOCAL_MODULE_PATH := $(TARGET_OUT_PRODUCT)/overlay
LOCAL_DEX_PREOPT := false
LOCAL_REPLACE_PREBUILT_APK_INSTALLED := $(LOCAL_PATH)/LeicaCameraMT6768Overlay.apk
include $(BUILD_PREBUILT)

include $(CLEAR_VARS)
LOCAL_MODULE := privapp-permissions-leica-mt6768
LOCAL_MODULE_CLASS := ETC
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE_STEM := privapp-permissions-leica-mt6768.xml
LOCAL_SRC_FILES := privapp-permissions-leica-mt6768.xml
LOCAL_MODULE_PATH := $(TARGET_OUT_ETC)/permissions
include $(BUILD_PREBUILT)

include $(CLEAR_VARS)
LOCAL_MODULE := leica-mt6768-hiddenapi
LOCAL_MODULE_CLASS := ETC
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE_STEM := leica-mt6768-hiddenapi.xml
LOCAL_SRC_FILES := leica-mt6768-hiddenapi.xml
LOCAL_MODULE_PATH := $(TARGET_OUT_ETC)/sysconfig
include $(BUILD_PREBUILT)

leica_jni_files :=
leica_jni_modules :=
leica_app_jni :=
endif
