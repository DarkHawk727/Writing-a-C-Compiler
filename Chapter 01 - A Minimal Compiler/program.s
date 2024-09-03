_main:
	pushq  %rbp
	movq  %rsp, %rbp
	movl  $42, %eax
	popq  %rbp
	retq
