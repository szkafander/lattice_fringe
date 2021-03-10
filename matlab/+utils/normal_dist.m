function d= normal_dist(P1, P2, P)
%this function computes the distance(d) of a point 'P'(x0,y0) from a line passing through
%two known points P1(x1,y1) and P2(x2,y2). it uses the formula
%d=asb((P2(1)-P1(1))*(P1(2)-P(2))-(P1(1)-P(1))*(P2(2)-P1(2)))/sqrt((P2(1)-P1(1))^2+(P2(2)-P1(2))^2)
%that is d=|(x2-x1)(y1-y0)-(x1-x0)(y2-y1)|/sqrt((x2-x1)^2+(y2-y1)^2).

d=abs((P2(1)-P1(1))*(P1(2)-P(2))-(P1(1)-P(1))*(P2(2)-P1(2)))/sqrt((P2(1)-P1(1))^2 +(P2(2)-P1(2))^2);
return