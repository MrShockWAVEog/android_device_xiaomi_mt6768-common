# Additional MT6768 device-specific log tags

ifeq (eng,$(TARGET_BUILD_VARIANT))
VENDOR_LOG_LEVEL := I
else
VENDOR_LOG_LEVEL := S
endif

PRODUCT_VENDOR_PROPERTIES += \
    persist.log.tag.powerhal-libperfmgr=$(VENDOR_LOG_LEVEL) \
    persist.log.tag.AAL=$(VENDOR_LOG_LEVEL) \
    persist.log.tag.Accelerometer=$(VENDOR_LOG_LEVEL) \
    persist.log.tag.fpc_tac=$(VENDOR_LOG_LEVEL) \
    persist.log.tag.fpc_fingerprint_hal=$(VENDOR_LOG_LEVEL) \
    persist.log.tag.fpc_hal_extension=$(VENDOR_LOG_LEVEL) \
    persist.log.tag.VirtualHalConfig=$(VENDOR_LOG_LEVEL) \
    persist.log.tag.android.hardware.biometrics.fingerprint-service.xiaomi=$(VENDOR_LOG_LEVEL)
