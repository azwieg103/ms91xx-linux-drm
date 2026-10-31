/* Copyright (C) 2023 MacroSilicon Technology Co., Ltd.
 *
 * This software is licensed under the terms of the GNU General Public
 * License version 2, as published by the Free Software Foundation, and
 * may be copied, distributed, and modified under those terms.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * msdisp_plat_dev.c -- Drm driver for MacroSilicon chip 913x and 912x
 */


#include <linux/version.h>
#include <linux/dma-mapping.h>
#include <linux/platform_device.h>
#include <linux/slab.h>
#if KERNEL_VERSION(5, 9, 0) <= LINUX_VERSION_CODE || defined(EL8)
#include <linux/iommu.h>
#endif

#include "msdisp_plat_drv.h"
#include "msdisp_plat_dev.h"
#include "msdisp_drm_drv.h"


struct platform_device *msdisp_platform_dev_create(struct platform_device_info *info)
{
	struct platform_device *platform_dev = NULL;

	platform_dev = platform_device_register_full(info);
	if (IS_ERR(platform_dev))
		return platform_dev;

	if (dma_set_mask(&platform_dev->dev, DMA_BIT_MASK(64))) {
		dev_warn(&platform_dev->dev, "Unable to change dma mask to 64 bit. ");
		dev_warn(&platform_dev->dev, "Sticking with 32 bit\\n");
	}

	dev_info(&platform_dev->dev, "Msdisp platform_device create\\n");

	return platform_dev;
}

void msdisp_platform_dev_destroy(struct platform_device *dev)
{
	platform_device_unregister(dev);
}

int msdisp_platform_device_probe(struct platform_device *pdev)
{
	struct drm_device *dev;

	/*
	 * Older kernels used archdata.iommu for the Intel IOMMU dummy-domain
	 * workaround.  On newer kernels, dev->iommu is kernel-managed
	 * (allocated and freed by the IOMMU core); never replace it with
	 * driver-owned or stack storage.
	 */
#if KERNEL_VERSION(5, 9, 0) > LINUX_VERSION_CODE && defined(CONFIG_INTEL_IOMMU)
#define INTEL_IOMMU_DUMMY_DOMAIN                ((void *)-1)
	pdev->dev.archdata.iommu = INTEL_IOMMU_DUMMY_DOMAIN;
#endif

	dev = msdisp_drm_device_create(&pdev->dev);
	if (IS_ERR_OR_NULL(dev))
		goto err_free;

	platform_set_drvdata(pdev, dev);
	return PTR_ERR_OR_ZERO(dev);

err_free:
	return PTR_ERR_OR_ZERO(dev);
}

#if KERNEL_VERSION(6, 11, 0) <= LINUX_VERSION_CODE
/* platform_driver.remove returns void since 6.11 */
void msdisp_platform_device_remove(struct platform_device *pdev)
{
	struct drm_device *drm = platform_get_drvdata(pdev);

	msdisp_drm_device_remove(drm);
}
#else
int msdisp_platform_device_remove(struct platform_device *pdev)
{
	struct drm_device *drm = platform_get_drvdata(pdev);

	msdisp_drm_device_remove(drm);
	return 0;
}
#endif
