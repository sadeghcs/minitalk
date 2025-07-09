/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   error.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: snasiri <snasiri@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/07/09 12:18:45 by snasiri           #+#    #+#             */
/*   Updated: 2025/07/09 12:23:47 by snasiri          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "utils.h"

void	handle_server_error(int error_code)
{
	if (error_code == ERR_ACK)
		write(2, "[Server] Error: Failed to send ACK signal.\n", 43);
	else if (error_code == ERR_END)
		write(2, "[Server] Error: Failed to send END signal.\n", 43);
	exit(EXIT_FAILURE);
}

void	handle_client_error(const char *msg)
{
	write(2, msg, ft_strlen(msg));
	exit(EXIT_FAILURE);
}
