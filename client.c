/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   client.c                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: snasiri <snasiri@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/06/27 16:46:22 by snasiri           #+#    #+#             */
/*   Updated: 2025/07/09 13:42:24 by snasiri          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "utils.h"

volatile sig_atomic_t	g_ack_received;

static void	signal_handler(int sig)
{
	if (sig == SIGUSR1)
		g_ack_received = 1;
	else if (sig == SIGUSR2)
		ft_putstr("[Client] Server confirmed message receipt.\n");
}

static void	send_signal(pid_t pid, int sig)
{
	if (kill(pid, sig) == -1)
		handle_client_error("[Client] Error: Failed to send signal.\n");
}

void	send_char(pid_t pid, char c)
{
	int	bit;

	bit = 7;
	while (bit >= 0)
	{
		g_ack_received = 0;
		if ((c >> bit) & 1)
			send_signal(pid, SIGUSR2);
		else
			send_signal(pid, SIGUSR1);
		while (!g_ack_received)
			pause();
		sleep(0);
		bit--;
	}
}

int	setup_and_validate(int argc, char **argv, pid_t *pid)
{
	struct sigaction	sa;

	if (argc != 3)
	{
		ft_putstr("Usage: ./client [server_pid] [message]\n");
		return (1);
	}
	*pid = ft_atoi(argv[1]);
	if (*pid <= 0)
	{
		ft_putstr("[Client] Error: Invalid PID.\n");
		return (1);
	}
	sa.sa_handler = signal_handler;
	sigemptyset(&sa.sa_mask);
	sa.sa_flags = 0;
	sigaction(SIGUSR1, &sa, NULL);
	sigaction(SIGUSR2, &sa, NULL);
	return (0);
}

int	main(int argc, char **argv)
{
	pid_t	pid;
	size_t	i;
	char	*msg;

	if (setup_and_validate(argc, argv, &pid))
		return (1);
	msg = argv[2];
	if (msg[0] == '\0')
	{
		ft_putstr("Warning: Message is empty. Nothing to send.\n");
		return (1);
	}
	i = 0;
	while (msg[i])
		send_char(pid, msg[i++]);
	send_char(pid, '\0');
	return (0);
}
