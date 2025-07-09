# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: snasiri <snasiri@student.42.fr>            +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/06/25 13:09:51 by snasiri           #+#    #+#              #
#    Updated: 2025/07/09 12:30:56 by snasiri          ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

NAME_SERVER = server
NAME_CLIENT = client


SRCS_UTILS = utils.c error.c
OBJS_UTILS = $(SRCS_UTILS:.c=.o)

all: $(NAME_SERVER) $(NAME_CLIENT)

$(NAME_SERVER): server.c $(OBJS_UTILS)
	cc -Wall -Wextra -Werror -o $(NAME_SERVER) server.c $(OBJS_UTILS)

$(NAME_CLIENT): client.c $(OBJS_UTILS)
	cc -Wall -Wextra -Werror -o $(NAME_CLIENT) client.c $(OBJS_UTILS)

clean:
	rm -f $(OBJS_UTILS)

fclean: clean
	rm -f $(NAME_SERVER) $(NAME_CLIENT)

re: fclean all

.PHONY: all clean fclean re
