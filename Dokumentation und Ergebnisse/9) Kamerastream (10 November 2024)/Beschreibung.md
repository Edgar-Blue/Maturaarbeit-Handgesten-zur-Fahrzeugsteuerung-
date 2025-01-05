Ein simples Programm soll zeigen, dass der Kamerastream separat von den Hauptprogrammen funktionieren kann und diese nicht verlangsamt. Mithilfe von Threading ist es möglich, Prozesse voneinander zu trennen, sodass sie unabhängig voneinander ablaufen und sich nicht gegenseitig behindern.

Der Hauptprozess (der „Stamm“) ist hier die konstante Kamerabewegung, während der Thread den Stream darstellt, der auf dem Desktop des Raspberry Pi 4 angezeigt wird.
