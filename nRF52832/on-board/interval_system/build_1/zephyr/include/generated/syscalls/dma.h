/* auto-generated by gen_syscalls.py, don't edit */

#ifndef Z_INCLUDE_SYSCALLS_DMA_H
#define Z_INCLUDE_SYSCALLS_DMA_H


#include <zephyr/tracing/tracing_syscall.h>

#ifndef _ASMLANGUAGE

#include <stdarg.h>

#include <syscall_list.h>
#include <zephyr/syscall.h>

#include <zephyr/linker/sections.h>


#ifdef __cplusplus
extern "C" {
#endif

extern int z_impl_dma_start(const struct device * dev, uint32_t channel);

__pinned_func
static inline int dma_start(const struct device * dev, uint32_t channel)
{
#ifdef CONFIG_USERSPACE
	if (z_syscall_trap()) {
		union { uintptr_t x; const struct device * val; } parm0 = { .val = dev };
		union { uintptr_t x; uint32_t val; } parm1 = { .val = channel };
		return (int) arch_syscall_invoke2(parm0.x, parm1.x, K_SYSCALL_DMA_START);
	}
#endif
	compiler_barrier();
	return z_impl_dma_start(dev, channel);
}

#if defined(CONFIG_TRACING_SYSCALL)
#ifndef DISABLE_SYSCALL_TRACING

#define dma_start(dev, channel) ({ 	int syscall__retval; 	sys_port_trace_syscall_enter(K_SYSCALL_DMA_START, dma_start, dev, channel); 	syscall__retval = dma_start(dev, channel); 	sys_port_trace_syscall_exit(K_SYSCALL_DMA_START, dma_start, dev, channel, syscall__retval); 	syscall__retval; })
#endif
#endif


extern int z_impl_dma_stop(const struct device * dev, uint32_t channel);

__pinned_func
static inline int dma_stop(const struct device * dev, uint32_t channel)
{
#ifdef CONFIG_USERSPACE
	if (z_syscall_trap()) {
		union { uintptr_t x; const struct device * val; } parm0 = { .val = dev };
		union { uintptr_t x; uint32_t val; } parm1 = { .val = channel };
		return (int) arch_syscall_invoke2(parm0.x, parm1.x, K_SYSCALL_DMA_STOP);
	}
#endif
	compiler_barrier();
	return z_impl_dma_stop(dev, channel);
}

#if defined(CONFIG_TRACING_SYSCALL)
#ifndef DISABLE_SYSCALL_TRACING

#define dma_stop(dev, channel) ({ 	int syscall__retval; 	sys_port_trace_syscall_enter(K_SYSCALL_DMA_STOP, dma_stop, dev, channel); 	syscall__retval = dma_stop(dev, channel); 	sys_port_trace_syscall_exit(K_SYSCALL_DMA_STOP, dma_stop, dev, channel, syscall__retval); 	syscall__retval; })
#endif
#endif


extern int z_impl_dma_suspend(const struct device * dev, uint32_t channel);

__pinned_func
static inline int dma_suspend(const struct device * dev, uint32_t channel)
{
#ifdef CONFIG_USERSPACE
	if (z_syscall_trap()) {
		union { uintptr_t x; const struct device * val; } parm0 = { .val = dev };
		union { uintptr_t x; uint32_t val; } parm1 = { .val = channel };
		return (int) arch_syscall_invoke2(parm0.x, parm1.x, K_SYSCALL_DMA_SUSPEND);
	}
#endif
	compiler_barrier();
	return z_impl_dma_suspend(dev, channel);
}

#if defined(CONFIG_TRACING_SYSCALL)
#ifndef DISABLE_SYSCALL_TRACING

#define dma_suspend(dev, channel) ({ 	int syscall__retval; 	sys_port_trace_syscall_enter(K_SYSCALL_DMA_SUSPEND, dma_suspend, dev, channel); 	syscall__retval = dma_suspend(dev, channel); 	sys_port_trace_syscall_exit(K_SYSCALL_DMA_SUSPEND, dma_suspend, dev, channel, syscall__retval); 	syscall__retval; })
#endif
#endif


extern int z_impl_dma_resume(const struct device * dev, uint32_t channel);

__pinned_func
static inline int dma_resume(const struct device * dev, uint32_t channel)
{
#ifdef CONFIG_USERSPACE
	if (z_syscall_trap()) {
		union { uintptr_t x; const struct device * val; } parm0 = { .val = dev };
		union { uintptr_t x; uint32_t val; } parm1 = { .val = channel };
		return (int) arch_syscall_invoke2(parm0.x, parm1.x, K_SYSCALL_DMA_RESUME);
	}
#endif
	compiler_barrier();
	return z_impl_dma_resume(dev, channel);
}

#if defined(CONFIG_TRACING_SYSCALL)
#ifndef DISABLE_SYSCALL_TRACING

#define dma_resume(dev, channel) ({ 	int syscall__retval; 	sys_port_trace_syscall_enter(K_SYSCALL_DMA_RESUME, dma_resume, dev, channel); 	syscall__retval = dma_resume(dev, channel); 	sys_port_trace_syscall_exit(K_SYSCALL_DMA_RESUME, dma_resume, dev, channel, syscall__retval); 	syscall__retval; })
#endif
#endif


extern int z_impl_dma_request_channel(const struct device * dev, void * filter_param);

__pinned_func
static inline int dma_request_channel(const struct device * dev, void * filter_param)
{
#ifdef CONFIG_USERSPACE
	if (z_syscall_trap()) {
		union { uintptr_t x; const struct device * val; } parm0 = { .val = dev };
		union { uintptr_t x; void * val; } parm1 = { .val = filter_param };
		return (int) arch_syscall_invoke2(parm0.x, parm1.x, K_SYSCALL_DMA_REQUEST_CHANNEL);
	}
#endif
	compiler_barrier();
	return z_impl_dma_request_channel(dev, filter_param);
}

#if defined(CONFIG_TRACING_SYSCALL)
#ifndef DISABLE_SYSCALL_TRACING

#define dma_request_channel(dev, filter_param) ({ 	int syscall__retval; 	sys_port_trace_syscall_enter(K_SYSCALL_DMA_REQUEST_CHANNEL, dma_request_channel, dev, filter_param); 	syscall__retval = dma_request_channel(dev, filter_param); 	sys_port_trace_syscall_exit(K_SYSCALL_DMA_REQUEST_CHANNEL, dma_request_channel, dev, filter_param, syscall__retval); 	syscall__retval; })
#endif
#endif


extern void z_impl_dma_release_channel(const struct device * dev, uint32_t channel);

__pinned_func
static inline void dma_release_channel(const struct device * dev, uint32_t channel)
{
#ifdef CONFIG_USERSPACE
	if (z_syscall_trap()) {
		union { uintptr_t x; const struct device * val; } parm0 = { .val = dev };
		union { uintptr_t x; uint32_t val; } parm1 = { .val = channel };
		(void) arch_syscall_invoke2(parm0.x, parm1.x, K_SYSCALL_DMA_RELEASE_CHANNEL);
		return;
	}
#endif
	compiler_barrier();
	z_impl_dma_release_channel(dev, channel);
}

#if defined(CONFIG_TRACING_SYSCALL)
#ifndef DISABLE_SYSCALL_TRACING

#define dma_release_channel(dev, channel) do { 	sys_port_trace_syscall_enter(K_SYSCALL_DMA_RELEASE_CHANNEL, dma_release_channel, dev, channel); 	dma_release_channel(dev, channel); 	sys_port_trace_syscall_exit(K_SYSCALL_DMA_RELEASE_CHANNEL, dma_release_channel, dev, channel); } while(false)
#endif
#endif


extern int z_impl_dma_chan_filter(const struct device * dev, int channel, void * filter_param);

__pinned_func
static inline int dma_chan_filter(const struct device * dev, int channel, void * filter_param)
{
#ifdef CONFIG_USERSPACE
	if (z_syscall_trap()) {
		union { uintptr_t x; const struct device * val; } parm0 = { .val = dev };
		union { uintptr_t x; int val; } parm1 = { .val = channel };
		union { uintptr_t x; void * val; } parm2 = { .val = filter_param };
		return (int) arch_syscall_invoke3(parm0.x, parm1.x, parm2.x, K_SYSCALL_DMA_CHAN_FILTER);
	}
#endif
	compiler_barrier();
	return z_impl_dma_chan_filter(dev, channel, filter_param);
}

#if defined(CONFIG_TRACING_SYSCALL)
#ifndef DISABLE_SYSCALL_TRACING

#define dma_chan_filter(dev, channel, filter_param) ({ 	int syscall__retval; 	sys_port_trace_syscall_enter(K_SYSCALL_DMA_CHAN_FILTER, dma_chan_filter, dev, channel, filter_param); 	syscall__retval = dma_chan_filter(dev, channel, filter_param); 	sys_port_trace_syscall_exit(K_SYSCALL_DMA_CHAN_FILTER, dma_chan_filter, dev, channel, filter_param, syscall__retval); 	syscall__retval; })
#endif
#endif


#ifdef __cplusplus
}
#endif

#endif
#endif /* include guard */
