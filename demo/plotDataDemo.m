clear
load('data1.mat')
load('data2.mat')
load('data3.mat')
subplot(1,3,1)
surf(S01, T1.*252, price1)
xlabel('Stock Price')
ylabel('Days till Expiry')
zlabel('Option Price')
shading interp
axis square
subplot(1,3,2)
surf(S02, vol2, price2)
xlabel('Stock Price')
ylabel('IV of ATM call')
zlabel('Option Price')
shading interp
axis square
subplot(1,3,3)
surf(vol3, T3.*252, price3)
xlabel('IV of ATM call')
ylabel('Days till Expiry')
zlabel('Option Price')
shading interp
axis square
sgtitle('Reverse Iron Butterfly Spread')