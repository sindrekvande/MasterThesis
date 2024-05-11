/* auto-generated by gen_syscalls.py, don't edit */

#ifndef Z_INCLUDE_SYSCALLS_SDHC_H
#define Z_INCLUDE_SYSCALLS_SDHC_H


#include <zephyr/tracing/tracing_syscall.h>

#ifndef _ASMLANGUAGE

#include <stdarg.h>

#include <syscall_list.h>
#include <zephyr/syscall.h>

#include <zephyr/linker/sections.h>


#ifdef __cplusplus
extern "C" {
#endif

extern int z_impl_sdhc_hw_reset(const struct device * dev);

__pinned_func
static inline int sdhc_hw_reset(const struct device * dev)
{
#ifdef CONFIG_USERSPACE
	if (z_syscall_trap()) {
		union { uintptr_t x; const struct device * val; } parm0 = { .val = dev };
		return (int) arch_syscall_invoke1(parm0.x, K_SYSCALL_SDHC_HW_RESET);
	}
#endif
	compiler_barrier();
	return z_impl_sdhc_hw_reset(dev);
}

#if defined(CONFIG_TRACING_SYSCALL)
#ifndef DISABLE_SYSCALL_TRACING

#define sdhc_hw_reset(dev) ({ 	int syscall__retval; 	sys_port_trace_syscall_enter(K_SYSCALL_SDHC_HW_RESET, sdhc_hw_reset, dev); 	syscall__retval = sdhc_hw_reset(dev); 	sys_port_trace_syscall_exit(K_SYSCALL_SDHC_HW_RESET, sdhc_hw_reset, dev, syscall__retval); 	syscall__retval; })
#endif
#endif


extern int z_impl_sdhc_request(const struct device * dev, struct sdhc_command * cmd, struct sdhc_data * data);

__pinned_func
static inline int sdhc_request(const struct device * dev, struct sdhc_command * cmd, struct sdhc_data * data)
{
#ifdef CONFIG_USERSPACE
	if (z_syscall_trap()) {
		union { uintptr_t x; const struct device * val; } parm0 = { .val = dev };
		union { uintptr_t x; struct sdhc_command * val; } parm1 = { .val = cmd };
		union { uintptr_t x; struct sdhc_data * val; } parm2 = { .val = data };
		return (int) arch_syscall_invoke3(parm0.x, parm1.x, parm2.x, K_SYSCALL_SDHC_REQUEST);
	}
#endif
	compiler_barrier();
	return z_impl_sdhc_request(dev, cmd, data);
}

#if defined(CONFIG_TRACING_SYSCALL)
#ifndef DISABLE_SYSCALL_TRACING

#define sdhc_request(dev, cmd, data) ({ 	int syscall__retval; 	sys_port_trace_syscall_enter(K_SYSCALL_SDHC_REQUEST, sdhc_request, dev, cmd, data); 	syscall__retval = sdhc_request(dev, cmd, data); 	sys_port_trace_syscall_exit(K_SYSCALL_SDHC_REQUEST, sdhc_request, dev, cmd, data, syscall__retval); 	syscall__retval; })
#endif
#endif


extern int z_impl_sdhc_set_io(const struct device * dev, struct sdhc_io * io);

__pinned_func
static inline int sdhc_set_io(const struct device * dev, struct sdhc_io * io)
{
#ifdef CONFIG_USERSPACE
	if (z_syscall_trap()) {
		union { uintptr_t x; const struct device * val; } parm0 = { .val = dev };
		union { uintptr_t x; struct sdhc_io * val; } parm1 = { .val = io };
		return (int) arch_syscall_invoke2(parm0.x, parm1.x, K_SYSCALL_SDHC_SET_IO);
	}
#endif
	compiler_barrier();
	return z_impl_sdhc_set_io(dev, io);
}

#if defined(CONFIG_TRACING_SYSCALL)
#ifndef DISABLE_SYSCALL_TRACING

#define sdhc_set_io(dev, io) ({ 	int syscall__retval; 	sys_port_trace_syscall_enter(K_SYSCALL_SDHC_SET_IO, sdhc_set_io, dev, io); 	syscall__retval = sdhc_set_io(dev, io); 	sys_port_trace_syscall_exit(K_SYSCALL_SDHC_SET_IO, sdhc_set_io, dev, io, syscall__retval); 	syscall__retval; })
#endif
#endif


extern int z_impl_sdhc_card_present(const struct device * dev);

__pinned_func
static inline int sdhc_card_present(const struct device * dev)
{
#ifdef CONFIG_USERSPACE
	if (z_syscall_trap()) {
		union { uintptr_t x; const struct device * val; } parm0 = { .val = dev };
		return (int) arch_syscall_invoke1(parm0.x, K_SYSCALL_SDHC_CARD_PRESENT);
	}
#endif
	compiler_barrier();
	return z_impl_sdhc_card_present(dev);
}

#if defined(CONFIG_TRACING_SYSCALL)
#ifndef DISABLE_SYSCALL_TRACING

#define sdhc_card_present(dev) ({ 	int syscall__retval; 	sys_port_trace_syscall_enter(K_SYSCALL_SDHC_CARD_PRESENT, sdhc_card_present, dev); 	syscall__retval = sdhc_card_present(dev); 	sys_port_trace_syscall_exit(K_SYSCALL_SDHC_CARD_PRESENT, sdhc_card_present, dev, syscall__retval); 	syscall__retval; })
#endif
#endif


extern int z_impl_sdhc_execute_tuning(const struct device * dev);

__pinned_func
static inline int sdhc_execute_tuning(const struct device * dev)
{
#ifdef CONFIG_USERSPACE
	if (z_syscall_trap()) {
		union { uintptr_t x; const struct device * val; } parm0 = { .val = dev };
		return (int) arch_syscall_invoke1(parm0.x, K_SYSCALL_SDHC_EXECUTE_TUNING);
	}
#endif
	compiler_barrier();
	return z_impl_sdhc_execute_tuning(dev);
}

#if defined(CONFIG_TRACING_SYSCALL)
#ifndef DISABLE_SYSCALL_TRACING

#define sdhc_execute_tuning(dev) ({ 	int syscall__retval; 	sys_port_trace_syscall_enter(K_SYSCALL_SDHC_EXECUTE_TUNING, sdhc_execute_tuning, dev); 	syscall__retval = sdhc_execute_tuning(dev); 	sys_port_trace_syscall_exit(K_SYSCALL_SDHC_EXECUTE_TUNING, sdhc_execute_tuning, dev, syscall__retval); 	syscall__retval; })
#endif
#endif


extern int z_impl_sdhc_card_busy(const struct device * dev);

__pinned_func
static inline int sdhc_card_busy(const struct device * dev)
{
#ifdef CONFIG_USERSPACE
	if (z_syscall_trap()) {
		union { uintptr_t x; const struct device * val; } parm0 = { .val = dev };
		return (int) arch_syscall_invoke1(parm0.x, K_SYSCALL_SDHC_CARD_BUSY);
	}
#endif
	compiler_barrier();
	return z_impl_sdhc_card_busy(dev);
}

#if defined(CONFIG_TRACING_SYSCALL)
#ifndef DISABLE_SYSCALL_TRACING

#define sdhc_card_busy(dev) ({ 	int syscall__retval; 	sys_port_trace_syscall_enter(K_SYSCALL_SDHC_CARD_BUSY, sdhc_card_busy, dev); 	syscall__retval = sdhc_card_busy(dev); 	sys_port_trace_syscall_exit(K_SYSCALL_SDHC_CARD_BUSY, sdhc_card_busy, dev, syscall__retval); 	syscall__retval; })
#endif
#endif


extern int z_impl_sdhc_get_host_props(const struct device * dev, struct sdhc_host_props * props);

__pinned_func
static inline int sdhc_get_host_props(const struct device * dev, struct sdhc_host_props * props)
{
#ifdef CONFIG_USERSPACE
	if (z_syscall_trap()) {
		union { uintptr_t x; const struct device * val; } parm0 = { .val = dev };
		union { uintptr_t x; struct sdhc_host_props * val; } parm1 = { .val = props };
		return (int) arch_syscall_invoke2(parm0.x, parm1.x, K_SYSCALL_SDHC_GET_HOST_PROPS);
	}
#endif
	compiler_barrier();
	return z_impl_sdhc_get_host_props(dev, props);
}

#if defined(CONFIG_TRACING_SYSCALL)
#ifndef DISABLE_SYSCALL_TRACING

#define sdhc_get_host_props(dev, props) ({ 	int syscall__retval; 	sys_port_trace_syscall_enter(K_SYSCALL_SDHC_GET_HOST_PROPS, sdhc_get_host_props, dev, props); 	syscall__retval = sdhc_get_host_props(dev, props); 	sys_port_trace_syscall_exit(K_SYSCALL_SDHC_GET_HOST_PROPS, sdhc_get_host_props, dev, props, syscall__retval); 	syscall__retval; })
#endif
#endif


#ifdef __cplusplus
}
#endif

#endif
#endif /* include guard */
