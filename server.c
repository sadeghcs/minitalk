/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   server.c                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: snasiri <snasiri@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/07/09 12:10:48 by snasiri           #+#    #+#             */
/*   Updated: 2025/07/09 12:46:24 by snasiri          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "utils.h"

volatile sig_atomic_t	g_fatal_error;

static char	*append_char(char *src, char c, size_t len)
{
	char	*new;
	size_t	i;

	new = malloc(len + 2);
	if (!new)
		return (NULL);
	i = 0;
	if (src)
	{
		while (i < len)
		{
			new[i] = src[i];
			i++;
		}
	}
	new[len] = c;
	new[len + 1] = '\0';
	free(src);
	return (new);
}

static void	process_char(char c, pid_t client_pid)
{
	static char		*message = NULL;
	static size_t	len = 0;

	if (!message)
	{
		message = malloc(1);
		if (!message)
			exit(EXIT_FAILURE);
		message[0] = '\0';
	}
	message = append_char(message, c, len);
	if (!message)
		exit(EXIT_FAILURE);
	len++;
	if (c == '\0')
	{
		write(1, message, len - 1);
		write(1, "\n", 1);
		free(message);
		message = NULL;
		len = 0;
		if (kill(client_pid, SIGUSR2) == -1)
			g_fatal_error = ERR_END;
	}
}

void	handle_signal(int sig, siginfo_t *info, void *context)
{
	static int				bit_count = 0;
	static unsigned char	c = 0;

	(void)context;
	if (sig == SIGUSR2)
		c |= (1 << (7 - bit_count));
	bit_count++;
	if (bit_count == 8)
	{
		process_char(c, info->si_pid);
		bit_count = 0;
		c = 0;
	}
	if (kill(info->si_pid, SIGUSR1) == -1)
		g_fatal_error = ERR_ACK;
}

void	handle_sigint(int sig)
{
	(void)sig;
	write(1, "\n[Server] Shutting down.\n", 26);
	exit(EXIT_SUCCESS);
}

int	main(void)
{
	struct sigaction	sa;
	struct sigaction	sa_int;

	g_fatal_error = ERR_NONE;
	sa.sa_sigaction = handle_signal;
	sigemptyset(&sa.sa_mask);
	sa.sa_flags = SA_SIGINFO;
	sigaction(SIGUSR1, &sa, NULL);
	sigaction(SIGUSR2, &sa, NULL);
	sa_int.sa_handler = handle_sigint;
	sigemptyset(&sa_int.sa_mask);
	sa_int.sa_flags = 0;
	sigaction(SIGINT, &sa_int, NULL);
	ft_putstr("Server PID: ");
	ft_putnbr(getpid());
	ft_putstr("\n");
	while (1)
	{
		pause();
		if (g_fatal_error)
			handle_server_error(g_fatal_error);
	}
	return (0);
}
