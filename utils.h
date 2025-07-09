/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   utils.h                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: snasiri <snasiri@student.42.fr>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/06/23 15:52:59 by snasiri           #+#    #+#             */
/*   Updated: 2025/07/09 12:21:29 by snasiri          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef UTILS_H
# define UTILS_H

# define ERR_NONE 0
# define ERR_ACK 1
# define ERR_END 2

# define _POSIX_C_SOURCE 200809L

# include <unistd.h>
# include <stdlib.h>
# include <sys/types.h>
# include <signal.h>

void	ft_putstr(char *s);
void	ft_putnbr(int n);
int		ft_atoi(const char *str);
size_t	ft_strlen(const char *s);

void	handle_server_error(int error_code);
void	handle_client_error(const char *msg);

#endif
