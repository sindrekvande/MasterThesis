/* auto-generated by gen_syscalls.py, don't edit */

#ifndef Z_INCLUDE_SYSCALLS_FUEL_GAUGE_H
#define Z_INCLUDE_SYSCALLS_FUEL_GAUGE_H


#include <zephyr/tracing/tracing_syscall.h>

#ifndef _ASMLANGUAGE

#include <stdarg.h>

#include <syscall_list.h>
#include <zephyr/syscall.h>

#include <zephyr/linker/sections.h>


#ifdef __cplusplus
extern "C" {
#endif

extern int z_impl_fuel_gauge_get_prop(const struct device * dev, struct fuel_gauge_get_property * props, size_t props_len);

__pinned_func
static inline int fuel_gauge_get_prop(const struct device * dev, struct fuel_gauge_get_property * props, size_t props_len)
{
#ifdef CONFIG_USERSPACE
	if (z_syscall_trap()) {
		union { uintptr_t x; const struct device * val; } parm0 = { .val = dev };
		union { uintptr_t x; struct fuel_gauge_get_property * val; } parm1 = { .val = props };
		union { uintptr_t x; size_t val; } parm2 = { .val = props_len };
		return (int) arch_syscall_invoke3(parm0.x, parm1.x, parm2.x, K_SYSCALL_FUEL_GAUGE_GET_PROP);
	}
#endif
	compiler_barrier();
	return z_impl_fuel_gauge_get_prop(dev, props, props_len);
}

#if defined(CONFIG_TRACING_SYSCALL)
#ifndef DISABLE_SYSCALL_TRACING

#define fuel_gauge_get_prop(dev, props, props_len) ({ 	int syscall__retval; 	sys_port_trace_syscall_enter(K_SYSCALL_FUEL_GAUGE_GET_PROP, fuel_gauge_get_prop, dev, props, props_len); 	syscall__retval = fuel_gauge_get_prop(dev, props, props_len); 	sys_port_trace_syscall_exit(K_SYSCALL_FUEL_GAUGE_GET_PROP, fuel_gauge_get_prop, dev, props, props_len, syscall__retval); 	syscall__retval; })
#endif
#endif


extern int z_impl_fuel_gauge_set_prop(const struct device * dev, struct fuel_gauge_set_property * props, size_t props_len);

__pinned_func
static inline int fuel_gauge_set_prop(const struct device * dev, struct fuel_gauge_set_property * props, size_t props_len)
{
#ifdef CONFIG_USERSPACE
	if (z_syscall_trap()) {
		union { uintptr_t x; const struct device * val; } parm0 = { .val = dev };
		union { uintptr_t x; struct fuel_gauge_set_property * val; } parm1 = { .val = props };
		union { uintptr_t x; size_t val; } parm2 = { .val = props_len };
		return (int) arch_syscall_invoke3(parm0.x, parm1.x, parm2.x, K_SYSCALL_FUEL_GAUGE_SET_PROP);
	}
#endif
	compiler_barrier();
	return z_impl_fuel_gauge_set_prop(dev, props, props_len);
}

#if defined(CONFIG_TRACING_SYSCALL)
#ifndef DISABLE_SYSCALL_TRACING

#define fuel_gauge_set_prop(dev, props, props_len) ({ 	int syscall__retval; 	sys_port_trace_syscall_enter(K_SYSCALL_FUEL_GAUGE_SET_PROP, fuel_gauge_set_prop, dev, props, props_len); 	syscall__retval = fuel_gauge_set_prop(dev, props, props_len); 	sys_port_trace_syscall_exit(K_SYSCALL_FUEL_GAUGE_SET_PROP, fuel_gauge_set_prop, dev, props, props_len, syscall__retval); 	syscall__retval; })
#endif
#endif


extern int z_impl_fuel_gauge_get_buffer_prop(const struct device * dev, struct fuel_gauge_get_buffer_property * prop, void * dst, size_t dst_len);

__pinned_func
static inline int fuel_gauge_get_buffer_prop(const struct device * dev, struct fuel_gauge_get_buffer_property * prop, void * dst, size_t dst_len)
{
#ifdef CONFIG_USERSPACE
	if (z_syscall_trap()) {
		union { uintptr_t x; const struct device * val; } parm0 = { .val = dev };
		union { uintptr_t x; struct fuel_gauge_get_buffer_property * val; } parm1 = { .val = prop };
		union { uintptr_t x; void * val; } parm2 = { .val = dst };
		union { uintptr_t x; size_t val; } parm3 = { .val = dst_len };
		return (int) arch_syscall_invoke4(parm0.x, parm1.x, parm2.x, parm3.x, K_SYSCALL_FUEL_GAUGE_GET_BUFFER_PROP);
	}
#endif
	compiler_barrier();
	return z_impl_fuel_gauge_get_buffer_prop(dev, prop, dst, dst_len);
}

#if defined(CONFIG_TRACING_SYSCALL)
#ifndef DISABLE_SYSCALL_TRACING

#define fuel_gauge_get_buffer_prop(dev, prop, dst, dst_len) ({ 	int syscall__retval; 	sys_port_trace_syscall_enter(K_SYSCALL_FUEL_GAUGE_GET_BUFFER_PROP, fuel_gauge_get_buffer_prop, dev, prop, dst, dst_len); 	syscall__retval = fuel_gauge_get_buffer_prop(dev, prop, dst, dst_len); 	sys_port_trace_syscall_exit(K_SYSCALL_FUEL_GAUGE_GET_BUFFER_PROP, fuel_gauge_get_buffer_prop, dev, prop, dst, dst_len, syscall__retval); 	syscall__retval; })
#endif
#endif


extern int z_impl_fuel_gauge_battery_cutoff(const struct device * dev);

__pinned_func
static inline int fuel_gauge_battery_cutoff(const struct device * dev)
{
#ifdef CONFIG_USERSPACE
	if (z_syscall_trap()) {
		union { uintptr_t x; const struct device * val; } parm0 = { .val = dev };
		return (int) arch_syscall_invoke1(parm0.x, K_SYSCALL_FUEL_GAUGE_BATTERY_CUTOFF);
	}
#endif
	compiler_barrier();
	return z_impl_fuel_gauge_battery_cutoff(dev);
}

#if defined(CONFIG_TRACING_SYSCALL)
#ifndef DISABLE_SYSCALL_TRACING

#define fuel_gauge_battery_cutoff(dev) ({ 	int syscall__retval; 	sys_port_trace_syscall_enter(K_SYSCALL_FUEL_GAUGE_BATTERY_CUTOFF, fuel_gauge_battery_cutoff, dev); 	syscall__retval = fuel_gauge_battery_cutoff(dev); 	sys_port_trace_syscall_exit(K_SYSCALL_FUEL_GAUGE_BATTERY_CUTOFF, fuel_gauge_battery_cutoff, dev, syscall__retval); 	syscall__retval; })
#endif
#endif


#ifdef __cplusplus
}
#endif

#endif
#endif /* include guard */
