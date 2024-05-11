/* auto-generated by gen_syscalls.py, don't edit */

#ifndef Z_INCLUDE_SYSCALLS_RAND32_H
#define Z_INCLUDE_SYSCALLS_RAND32_H


#include <zephyr/tracing/tracing_syscall.h>

#ifndef _ASMLANGUAGE

#include <stdarg.h>

#include <syscall_list.h>
#include <zephyr/syscall.h>

#include <zephyr/linker/sections.h>


#ifdef __cplusplus
extern "C" {
#endif

extern uint32_t z_impl_sys_rand32_get(void);

__pinned_func
static inline uint32_t sys_rand32_get(void)
{
#ifdef CONFIG_USERSPACE
	if (z_syscall_trap()) {
		return (uint32_t) arch_syscall_invoke0(K_SYSCALL_SYS_RAND32_GET);
	}
#endif
	compiler_barrier();
	return z_impl_sys_rand32_get();
}

#if defined(CONFIG_TRACING_SYSCALL)
#ifndef DISABLE_SYSCALL_TRACING

#define sys_rand32_get() ({ 	uint32_t syscall__retval; 	sys_port_trace_syscall_enter(K_SYSCALL_SYS_RAND32_GET, sys_rand32_get); 	syscall__retval = sys_rand32_get(); 	sys_port_trace_syscall_exit(K_SYSCALL_SYS_RAND32_GET, sys_rand32_get, syscall__retval); 	syscall__retval; })
#endif
#endif


extern void z_impl_sys_rand_get(void * dst, size_t len);

__pinned_func
static inline void sys_rand_get(void * dst, size_t len)
{
#ifdef CONFIG_USERSPACE
	if (z_syscall_trap()) {
		union { uintptr_t x; void * val; } parm0 = { .val = dst };
		union { uintptr_t x; size_t val; } parm1 = { .val = len };
		(void) arch_syscall_invoke2(parm0.x, parm1.x, K_SYSCALL_SYS_RAND_GET);
		return;
	}
#endif
	compiler_barrier();
	z_impl_sys_rand_get(dst, len);
}

#if defined(CONFIG_TRACING_SYSCALL)
#ifndef DISABLE_SYSCALL_TRACING

#define sys_rand_get(dst, len) do { 	sys_port_trace_syscall_enter(K_SYSCALL_SYS_RAND_GET, sys_rand_get, dst, len); 	sys_rand_get(dst, len); 	sys_port_trace_syscall_exit(K_SYSCALL_SYS_RAND_GET, sys_rand_get, dst, len); } while(false)
#endif
#endif


extern int z_impl_sys_csrand_get(void * dst, size_t len);

__pinned_func
static inline int sys_csrand_get(void * dst, size_t len)
{
#ifdef CONFIG_USERSPACE
	if (z_syscall_trap()) {
		union { uintptr_t x; void * val; } parm0 = { .val = dst };
		union { uintptr_t x; size_t val; } parm1 = { .val = len };
		return (int) arch_syscall_invoke2(parm0.x, parm1.x, K_SYSCALL_SYS_CSRAND_GET);
	}
#endif
	compiler_barrier();
	return z_impl_sys_csrand_get(dst, len);
}

#if defined(CONFIG_TRACING_SYSCALL)
#ifndef DISABLE_SYSCALL_TRACING

#define sys_csrand_get(dst, len) ({ 	int syscall__retval; 	sys_port_trace_syscall_enter(K_SYSCALL_SYS_CSRAND_GET, sys_csrand_get, dst, len); 	syscall__retval = sys_csrand_get(dst, len); 	sys_port_trace_syscall_exit(K_SYSCALL_SYS_CSRAND_GET, sys_csrand_get, dst, len, syscall__retval); 	syscall__retval; })
#endif
#endif


#ifdef __cplusplus
}
#endif

#endif
#endif /* include guard */
