# SPDX-License-Identifier: Apache-2.0

# Mirror the MediaTek base/debug policy setup for VoltageOS. The upstream
# SEPolicy.mk hardcodes device/lineage/sepolicy for libperfmgr.
MTK_SEPOLICY_PATH := device/mediatek/sepolicy_vndr

include device/voltage/sepolicy/libperfmgr/sepolicy.mk

BOARD_VENDOR_SEPOLICY_DIRS += $(MTK_SEPOLICY_PATH)/base/vendor
SYSTEM_EXT_PRIVATE_SEPOLICY_DIRS += $(MTK_SEPOLICY_PATH)/base/private
SYSTEM_EXT_PUBLIC_SEPOLICY_DIRS += $(MTK_SEPOLICY_PATH)/base/public

ifneq ($(TARGET_BUILD_VARIANT),user)
BOARD_VENDOR_SEPOLICY_DIRS += $(MTK_SEPOLICY_PATH)/debug/vendor
SYSTEM_EXT_PRIVATE_SEPOLICY_DIRS += $(MTK_SEPOLICY_PATH)/debug/private
SYSTEM_EXT_PUBLIC_SEPOLICY_DIRS += $(MTK_SEPOLICY_PATH)/debug/public
endif
